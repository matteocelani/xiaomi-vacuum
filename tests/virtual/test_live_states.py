"""Dump entity states for one lab model. Temporary audit."""

from __future__ import annotations

from custom_components.xiaomi_robot_vacuum.const import (
    CONF_ACCOUNT_TYPE,
    CONF_MAC,
    CONF_NOTIFY,
    CONF_PREFER_CLOUD,
    CONF_VERSION,
    DOMAIN,
)
from custom_components.xiaomi_robot_vacuum.xiaomi.mapping import resolve_family
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry
from tests.virtual.fleet_catalog import robot_profiles
from tests.virtual.miio_endpoint import MiioEndpoint
from tests.virtual.spec_robot import SpecRobot
from tests.xiaomi.helpers import release_device

from homeassistant.const import CONF_HOST, CONF_MODEL, CONF_NAME, CONF_TOKEN
from homeassistant.core import HomeAssistant

_TOKEN = "00" * 16
_MAC = "00:00:00:00:00:00"

pytestmark = [
    pytest.mark.ha,
    pytest.mark.enable_socket,
    pytest.mark.allow_hosts(["127.0.0.1"]),
]


async def test_dump_live_states(
    hass: HomeAssistant,
    socket_enabled: None,
    enable_custom_integrations: None,
    integration_package: object,
) -> None:
    del socket_enabled, enable_custom_integrations, integration_package
    from custom_components.xiaomi_robot_vacuum.dreame import VERSION

    lines: list[str] = []
    for index, profile in enumerate(
        item for item in robot_profiles() if not item.submodel
    ):
        family = resolve_family(profile.model)
        assert family is not None
        mac = f"00:00:00:00:00:{index + 1:02x}"
        robot = SpecRobot(profile.model, profile.document(), mac=mac)
        robot.apply_family(family)
        code = profile.model.rsplit(".", 1)[-1]
        with MiioEndpoint(robot):
            entry = MockConfigEntry(
                domain=DOMAIN,
                unique_id=profile.model,
                data={
                    CONF_NAME: f"Lab {code}",
                    CONF_HOST: "127.0.0.1",
                    CONF_TOKEN: _TOKEN,
                    CONF_MAC: mac,
                    CONF_MODEL: profile.model,
                    CONF_ACCOUNT_TYPE: "mi",
                },
                options={
                    CONF_PREFER_CLOUD: False,
                    CONF_NOTIFY: False,
                    CONF_VERSION: VERSION,
                },
            )
            before = {state.entity_id for state in hass.states.async_all()}
            entry.add_to_hass(hass)
            assert await hass.config_entries.async_setup(entry.entry_id)
            await hass.async_block_till_done()
            device = hass.data[DOMAIN][entry.entry_id].device
            try:
                for state in hass.states.async_all():
                    if state.entity_id in before or state.domain == "button":
                        continue
                    if state.state not in {"unknown", "unavailable"}:
                        continue
                    suffix = state.entity_id.split(".", 1)[-1].removeprefix(
                        f"lab_{code}_"
                    )
                    lines.append(
                        f"{profile.model} {state.state} {state.domain}:{suffix}"
                    )
            finally:
                await hass.config_entries.async_unload(entry.entry_id)
                await hass.async_block_till_done()
                release_device(device)
    assert not lines, "\n".join(lines)

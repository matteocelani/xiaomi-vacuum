"""vacuum_reset_consumable uses the sweep button when the model publishes one."""

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
_MAC = "00:00:00:00:00:42"

pytestmark = [
    pytest.mark.ha,
    pytest.mark.enable_socket,
    pytest.mark.allow_hosts(["127.0.0.1"]),
]


async def test_sweep_reset_service_calls_the_published_button(
    hass: HomeAssistant,
    socket_enabled: None,
    enable_custom_integrations: None,
    integration_package: object,
) -> None:
    """main_brush on b112 is action 7/1, the sweep reset-consumable action."""
    del socket_enabled, enable_custom_integrations, integration_package
    from custom_components.xiaomi_robot_vacuum.dreame import VERSION

    profile = next(
        item
        for item in robot_profiles()
        if item.model == "xiaomi.vacuum.b112" and not item.submodel
    )
    family = resolve_family(profile.model)
    assert family is not None
    robot = SpecRobot(profile.model, profile.document(), mac=_MAC)
    robot.apply_family(family)
    with MiioEndpoint(robot):
        entry = MockConfigEntry(
            domain=DOMAIN,
            unique_id=profile.model,
            data={
                CONF_NAME: profile.model,
                CONF_HOST: "127.0.0.1",
                CONF_TOKEN: _TOKEN,
                CONF_MAC: _MAC,
                CONF_MODEL: profile.model,
                CONF_ACCOUNT_TYPE: "mi",
            },
            options={
                CONF_PREFER_CLOUD: False,
                CONF_NOTIFY: False,
                CONF_VERSION: VERSION,
            },
        )
        entry.add_to_hass(hass)
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        try:
            state = next(
                item for item in hass.states.async_all() if item.domain == "vacuum"
            )
            await hass.services.async_call(
                DOMAIN,
                "vacuum_reset_consumable",
                {"entity_id": state.entity_id, "consumable": "main_brush"},
                blocking=True,
            )
            assert (7, 1) in robot.actions
            assert any(
                isinstance(item, list) and {"piid": 17, "value": 1} in item
                for item in robot.action_inputs
            )
        finally:
            device = hass.data.get(DOMAIN, {}).get(entry.entry_id)
            device = getattr(device, "device", device)
            assert await hass.config_entries.async_unload(entry.entry_id)
            await hass.async_block_till_done()
            if device is not None:
                release_device(device)

"""Reload keeps a local entry connected for every canonical model."""

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
_MAC = "00:00:00:00:00:21"
_CANONICAL = tuple(profile for profile in robot_profiles() if not profile.submodel)

pytestmark = [
    pytest.mark.ha,
    pytest.mark.enable_socket,
    pytest.mark.allow_hosts(["127.0.0.1"]),
]


@pytest.mark.parametrize("profile", _CANONICAL, ids=lambda profile: profile.model)
async def test_reload_leaves_the_vacuum_docked(
    hass: HomeAssistant,
    socket_enabled: None,
    enable_custom_integrations: None,
    integration_package: object,
    profile: object,
) -> None:
    """Setup, reload, and the vacuum is still docked on the same entry."""
    del socket_enabled, enable_custom_integrations, integration_package
    from custom_components.xiaomi_robot_vacuum.dreame import VERSION

    model = profile.model
    family = resolve_family(model)
    assert family is not None
    robot = SpecRobot(model, profile.document(), mac=_MAC)
    robot.apply_family(family)
    with MiioEndpoint(robot):
        entry = MockConfigEntry(
            domain=DOMAIN,
            unique_id=model,
            data={
                CONF_NAME: model,
                CONF_HOST: "127.0.0.1",
                CONF_TOKEN: _TOKEN,
                CONF_MAC: _MAC,
                CONF_MODEL: model,
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
            assert _vacuum(hass).state == "docked"
            assert await hass.config_entries.async_reload(entry.entry_id)
            await hass.async_block_till_done()
            assert _vacuum(hass).state == "docked"
            await hass.services.async_call(
                "vacuum",
                "start",
                {"entity_id": _vacuum(hass).entity_id},
                blocking=True,
            )
            coordinator = hass.data[DOMAIN][entry.entry_id]
            await hass.async_add_executor_job(coordinator.device._request_properties)
            coordinator.async_set_updated_data()
            await hass.async_block_till_done()
            assert _vacuum(hass).state == "cleaning"
        finally:
            device = hass.data.get(DOMAIN, {}).get(entry.entry_id)
            device = getattr(device, "device", device)
            assert await hass.config_entries.async_unload(entry.entry_id)
            await hass.async_block_till_done()
            if device is not None:
                release_device(device)


def _vacuum(hass: HomeAssistant):
    states = [state for state in hass.states.async_all() if state.domain == "vacuum"]
    assert len(states) == 1
    return states[0]

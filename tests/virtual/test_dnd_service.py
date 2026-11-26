"""The do-not-disturb service reaches the sweep action and refuses other models."""

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
from homeassistant.exceptions import HomeAssistantError

_TOKEN = "00" * 16
_MAC = "00:00:00:00:00:41"
_FIELDS = {
    "enable": True,
    "start_hour": 22,
    "start_minute": 0,
    "end_hour": 7,
    "end_minute": 30,
}

pytestmark = [
    pytest.mark.ha,
    pytest.mark.enable_socket,
    pytest.mark.allow_hosts(["127.0.0.1"]),
]


async def _entry(hass: HomeAssistant, model: str) -> MockConfigEntry:
    from custom_components.xiaomi_robot_vacuum.dreame import VERSION

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
    return entry


async def _unload(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    device = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    device = getattr(device, "device", device)
    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    if device is not None:
        release_device(device)


async def test_sweep_dnd_service_calls_set_notdisturb(
    hass: HomeAssistant,
    socket_enabled: None,
    enable_custom_integrations: None,
    integration_package: object,
) -> None:
    """b112 accepts the service and the robot records action 12/1."""
    del socket_enabled, enable_custom_integrations, integration_package
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
        entry = await _entry(hass, profile.model)
        try:
            state = next(
                item for item in hass.states.async_all() if item.domain == "vacuum"
            )
            await hass.services.async_call(
                DOMAIN,
                "xiaomi_set_dnd",
                {"entity_id": state.entity_id, **_FIELDS},
                blocking=True,
            )
            assert (12, 1) in robot.actions
        finally:
            await _unload(hass, entry)


async def test_station_dnd_service_sends_nothing(
    hass: HomeAssistant,
    socket_enabled: None,
    enable_custom_integrations: None,
    integration_package: object,
) -> None:
    """A model without set-notdisturb is rejected before any action."""
    del socket_enabled, enable_custom_integrations, integration_package
    profile = next(
        item
        for item in robot_profiles()
        if item.model == "xiaomi.vacuum.b108gl" and not item.submodel
    )
    family = resolve_family(profile.model)
    assert family is not None
    robot = SpecRobot(profile.model, profile.document(), mac=_MAC)
    robot.apply_family(family)
    with MiioEndpoint(robot):
        entry = await _entry(hass, profile.model)
        try:
            state = next(
                item for item in hass.states.async_all() if item.domain == "vacuum"
            )
            with pytest.raises(HomeAssistantError):
                await hass.services.async_call(
                    DOMAIN,
                    "xiaomi_set_dnd",
                    {"entity_id": state.entity_id, **_FIELDS},
                    blocking=True,
                )
            assert (12, 1) not in robot.actions
        finally:
            await _unload(hass, entry)

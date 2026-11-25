"""Home Assistant setup against the spec robot for one model per family."""

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
from custom_components.xiaomi_robot_vacuum.xiaomi.model import StoredState
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry
from tests.virtual.fleet_catalog import representative_models, robot_profiles
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


@pytest.mark.parametrize(
    ("family_name", "model"),
    representative_models(),
    ids=[name for name, _model in representative_models()],
)
async def test_representative_family_exposes_vacuum_controls_and_a_fault(
    hass: HomeAssistant,
    socket_enabled: None,
    enable_custom_integrations: None,
    integration_package: object,
    family_name: str,
    model: str,
) -> None:
    """Each family docks, cleans, and reports the spec fault as an error state."""
    del enable_custom_integrations, integration_package, family_name
    # The device-core import stub hides dreame.VERSION until this fixture loads it.
    from custom_components.xiaomi_robot_vacuum.dreame import VERSION

    family = resolve_family(model)
    assert family is not None
    robot = SpecRobot(model, _document(model), mac=_MAC)
    robot.apply_family(family)
    with MiioEndpoint(robot):
        entry = MockConfigEntry(
            domain=DOMAIN,
            unique_id=model,
            data={
                CONF_NAME: f"Lab {model.rsplit('.', 1)[-1]}",
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
        device = hass.data[DOMAIN][entry.entry_id].device
        try:
            vacuum = _vacuum(hass)
            assert vacuum.state == "docked"
            battery = [
                state
                for state in hass.states.async_all()
                if state.attributes.get("device_class") == "battery"
            ]
            assert battery
            assert battery[0].state not in {"unknown", "unavailable", "None"}
            await hass.services.async_call(
                "vacuum",
                "start",
                {"entity_id": vacuum.entity_id},
                blocking=True,
            )
            await _refresh(hass, entry.entry_id)
            assert _vacuum(hass).state == "cleaning"
            await hass.services.async_call(
                "vacuum",
                "return_to_base",
                {"entity_id": vacuum.entity_id},
                blocking=True,
            )
            await _refresh(hass, entry.entry_id)
            assert _vacuum(hass).state == "docked"
            assert robot.set_fault() is not None
            robot.set_stored(StoredState.ERROR)
            await _refresh(hass, entry.entry_id)
            assert _vacuum(hass).state == "error"
        finally:
            assert await hass.config_entries.async_unload(entry.entry_id)
            await hass.async_block_till_done()
            release_device(device)


def _document(model: str) -> dict[str, object]:
    for profile in robot_profiles():
        if profile.model == model and not profile.submodel:
            return profile.document()
    raise KeyError(model)


def _vacuum(hass: HomeAssistant):
    states = [state for state in hass.states.async_all() if state.domain == "vacuum"]
    assert len(states) == 1
    return states[0]


async def _refresh(hass: HomeAssistant, entry_id: str) -> None:
    coordinator = hass.data[DOMAIN][entry_id]
    await hass.async_add_executor_job(coordinator.device._request_properties)
    coordinator.async_set_updated_data()
    await hass.async_block_till_done()

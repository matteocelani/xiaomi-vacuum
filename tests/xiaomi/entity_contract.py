"""Shared Home Assistant entity exercises for Xiaomi model tests."""

from __future__ import annotations

from collections.abc import Mapping
import contextlib
from dataclasses import dataclass
import sys
from typing import Final

from custom_components.dreame_vacuum.const import (
    CONF_ACCOUNT_TYPE,
    CONF_MAC,
    CONF_NOTIFY,
    CONF_PREFER_CLOUD,
    CONF_VERSION,
    DOMAIN,
)
from custom_components.dreame_vacuum.xiaomi.controls import XiaomiControl
from custom_components.dreame_vacuum.xiaomi.mapping import XiaomiModel
from custom_components.dreame_vacuum.xiaomi.model import StoredState
from pytest_homeassistant_custom_component.common import MockConfigEntry
from tests.xiaomi.helpers import FakeMiio, release_device, wire_for_state
from tests.xiaomi.spec_helpers import (
    LOOPBACK_HOST,
    LOOPBACK_MAC,
    LOOPBACK_TOKEN,
    assert_traffic_is_mapped,
    require_family,
)

from homeassistant.const import CONF_HOST, CONF_NAME, CONF_TOKEN
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er

_LEGACY_SWITCHES: Final = (
    "resume_cleaning",
    "carpet_boost",
    "child_lock",
    "dnd",
    "auto_dust_collecting",
)
_PROPERTY_BY_ENTITY: Final = {"charging_state": "CHARGING_STATUS"}
_LEGACY_RESET_BUTTONS: Final = (
    "reset_main_brush",
    "reset_side_brush",
    "reset_filter",
    "reset_mop_pad",
    "reset_detergent",
)


@dataclass(frozen=True, slots=True)
class EntityCase:
    """Registry expectation and sample wires for one model's entities."""

    model: str
    device_name: str
    entities: frozenset[tuple[str, str]]
    counter_samples: Mapping[str, tuple[object, str]]
    status_samples: Mapping[str, tuple[object, str]]
    consumable_life: tuple[str, ...]
    omitted_legacy_selects: frozenset[str] = frozenset()
    reports_charging: bool = True
    station_vacuum: bool = True


_MIJIA_B108_ENTITIES: Final[frozenset[tuple[str, str]]] = frozenset(
    {
        ("binary_sensor", "charging_state"),
        ("binary_sensor", "maintenance"),
        ("binary_sensor", "problem"),
        ("button", "reset_filter"),
        ("button", "reset_main_brush"),
        ("button", "reset_mop_pad"),
        ("button", "reset_side_brush"),
        ("number", "volume"),
        ("select", "cleaning_mode"),
        ("select", "suction_level"),
        ("select", "water_volume"),
        ("sensor", "battery_level"),
        ("sensor", "charging_status"),
        ("sensor", "cleaned_area"),
        ("sensor", "cleaning_time"),
        ("sensor", "error"),
        ("sensor", "filter_left"),
        ("sensor", "filter_time_left"),
        ("sensor", "firmware_version"),
        ("sensor", "main_brush_left"),
        ("sensor", "main_brush_time_left"),
        ("sensor", "mop_pad_left"),
        ("sensor", "mop_pad_time_left"),
        ("sensor", "relocation_status"),
        ("sensor", "side_brush_left"),
        ("sensor", "side_brush_time_left"),
        ("sensor", "state"),
        ("sensor", "task_status"),
        ("sensor", "water_tank"),
        ("switch", "carpet_boost"),
        ("switch", "child_lock"),
        ("switch", "dnd"),
        ("switch", "resume_cleaning"),
        ("vacuum", "dreame_vacuum"),
    }
)
_MIJIA_B108_COUNTERS: Final[dict[str, tuple[object, str]]] = {
    "BATTERY_LEVEL": (55, "55"),
    "CLEANED_AREA": (12, "12"),
    "CLEANING_TIME": (9, "9"),
    "MAIN_BRUSH_LEFT": (80, "80"),
    "MAIN_BRUSH_TIME_LEFT": (70, "70"),
    "SIDE_BRUSH_LEFT": (81, "81"),
    "SIDE_BRUSH_TIME_LEFT": (71, "71"),
    "FILTER_LEFT": (82, "82"),
    "FILTER_TIME_LEFT": (72, "72"),
    "MOP_PAD_LEFT": (83, "83"),
    "MOP_PAD_TIME_LEFT": (73, "73"),
    "ERROR": (0, "no_error"),
}
_MIJIA_B108_STATUS: Final[dict[str, tuple[object, str]]] = {
    "CHARGING_STATUS": (2, "not_charging"),
    "STATE": (1, "idle"),
    "TASK_STATUS": (1, "completed"),
    "RELOCATION_STATUS": (0, "located"),
    "WATER_TANK": (True, "installed"),
}
_MIJIA_B108_CONSUMABLE_LIFE: Final[tuple[str, ...]] = (
    "MAIN_BRUSH_LEFT",
    "SIDE_BRUSH_LEFT",
    "FILTER_LEFT",
    "MOP_PAD_LEFT",
)


def mijia_b108_entity_case(model: str, device_name: str) -> EntityCase:
    """Entity case shared by the released mijia.vacuum.b108 models."""
    return EntityCase(
        model=model,
        device_name=device_name,
        entities=_MIJIA_B108_ENTITIES,
        counter_samples=_MIJIA_B108_COUNTERS,
        status_samples=_MIJIA_B108_STATUS,
        consumable_life=_MIJIA_B108_CONSUMABLE_LIFE,
    )


async def exercise_home_assistant_entities(
    hass: HomeAssistant, case: EntityCase
) -> None:
    """Drive every entity this model creates and keep traffic on the map."""
    version = sys.modules["custom_components.dreame_vacuum.dreame"].VERSION
    family = require_family(case.model)
    with FakeMiio(case.model) as fake:
        entry = _entry(version, case.device_name)
        entry.add_to_hass(hass)
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        device = hass.data[DOMAIN][entry.entry_id].device
        try:
            _assert_registry(hass, entry.entry_id, family, case)
            await _exercise_selects_switches_number_and_buttons(
                hass, fake, family, case
            )
            await _exercise_vacuum_states(hass, entry.entry_id, fake, family, case)
            await _exercise_sensors(hass, entry.entry_id, fake, family, case)
            await _exercise_binary_sensors(hass, entry.entry_id, fake, family, case)
            await _exercise_controls(hass, entry.entry_id, fake, family)
        finally:
            assert await hass.config_entries.async_unload(entry.entry_id)
            await hass.async_block_till_done()
            release_device(device)
        assert_traffic_is_mapped(fake, family)


async def assert_entities_read_or_write(hass: HomeAssistant, case: EntityCase) -> None:
    """Assert each entity polls a mapped property or sends a mapped wire."""
    version = sys.modules["custom_components.dreame_vacuum.dreame"].VERSION
    family = require_family(case.model)
    with FakeMiio(case.model) as fake:
        entry = _entry(version, case.device_name + " Map")
        entry.add_to_hass(hass)
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        device = hass.data[DOMAIN][entry.entry_id].device
        try:
            keys = _registry_keys(hass, entry.entry_id)
            if ("switch", "dnd") not in case.entities:
                assert ("switch", "dnd") not in keys
            for domain, key in keys:
                if key.startswith("reset_"):
                    assert domain == "button"
                    assert key.upper() in family.action_overrides
            polled: list[tuple[int, int]] = []
            original = device._protocol.get_properties

            def record(
                parameters: list[dict[str, int]],
                retry_count: int = 1,
                timeout: object = None,
            ) -> list[dict[str, object]]:
                del retry_count, timeout
                polled.extend((item["siid"], item["piid"]) for item in parameters)
                return original(parameters)

            device._protocol.get_properties = record
            await _refresh(hass, entry.entry_id)
            seen = set(polled)
            controls = {control.key: control for control in family.controls}
            properties = {
                name: (item["siid"], item["piid"])
                for name, item in family.property_overrides.items()
            }
            for domain, key in keys:
                if domain == "vacuum":
                    await hass.services.async_call(
                        "vacuum",
                        "start",
                        {"entity_id": _entity_id(hass, entry.entry_id, "vacuum", key)},
                        blocking=True,
                    )
                    assert fake.actions[-1] == (
                        family.action_overrides["START"]["siid"],
                        family.action_overrides["START"]["aiid"],
                    )
                    assert properties["STATE"] in seen
                    continue
                if key == "firmware_version":
                    assert _state(hass, entry.entry_id, "sensor", key)
                    continue
                if key == "problem":
                    assert properties["ERROR"] in seen
                    continue
                if key == "maintenance":
                    for name in case.consumable_life:
                        assert properties[name] in seen
                    continue
                control = controls.get(key)
                if control is not None and str(control.domain) == domain:
                    if control.property_name:
                        address = properties[control.property_name]
                        assert address in seen
                        if control.writable and control.domain == "select":
                            fake.set_value(
                                address[0], address[1], control.options[-1][0]
                            )
                            await _refresh(hass, entry.entry_id)
                            await hass.services.async_call(
                                "select",
                                "select_option",
                                {
                                    "entity_id": _entity_id(
                                        hass, entry.entry_id, "select", key
                                    ),
                                    "option": control.options[0][1],
                                },
                                blocking=True,
                            )
                            assert fake.writes[-1] == (
                                address[0],
                                address[1],
                                control.options[0][0],
                            )
                        continue
                    if not control.readable and control.domain == "select":
                        await _enable_control(hass, entry.entry_id, control)
                        await hass.services.async_call(
                            "select",
                            "select_option",
                            {
                                "entity_id": _entity_id(
                                    hass, entry.entry_id, "select", key
                                ),
                                "option": control.options[0][1],
                            },
                            blocking=True,
                        )
                        assert fake.writes[-1] == (
                            control.siid,
                            control.piid,
                            control.options[0][0],
                        )
                        continue
                    if not control.readable and control.domain == "number":
                        await _enable_control(hass, entry.entry_id, control)
                        await hass.services.async_call(
                            "number",
                            "set_value",
                            {
                                "entity_id": _entity_id(
                                    hass, entry.entry_id, "number", key
                                ),
                                "value": control.minimum,
                            },
                            blocking=True,
                        )
                        assert fake.writes[-1][:2] == (control.siid, control.piid)
                        continue
                    if control.aiid is not None:
                        await hass.services.async_call(
                            "button",
                            "press",
                            {
                                "entity_id": _entity_id(
                                    hass, entry.entry_id, "button", key
                                )
                            },
                            blocking=True,
                        )
                        assert fake.actions[-1] == (control.siid, control.aiid)
                        assert fake.action_inputs[-1] == [
                            {"piid": piid, "value": value}
                            for piid, value in control.action_parameters
                        ]
                        continue
                    assert (control.siid, control.piid) in seen
                    if control.writable and control.domain == "number":
                        await hass.services.async_call(
                            "number",
                            "set_value",
                            {
                                "entity_id": _entity_id(
                                    hass, entry.entry_id, "number", key
                                ),
                                "value": control.minimum,
                            },
                            blocking=True,
                        )
                        assert fake.writes[-1][:2] == (control.siid, control.piid)
                    if control.writable and control.domain == "select":
                        fake.set_value(
                            control.siid, control.piid, control.options[0][0]
                        )
                        await _refresh(hass, entry.entry_id)
                        await hass.services.async_call(
                            "select",
                            "select_option",
                            {
                                "entity_id": _entity_id(
                                    hass, entry.entry_id, "select", key
                                ),
                                "option": control.options[0][1],
                            },
                            blocking=True,
                        )
                        assert fake.writes[-1] == (
                            control.siid,
                            control.piid,
                            control.options[0][0],
                        )
                    continue
                action_name = key.upper()
                if domain == "button" and action_name in family.action_overrides:
                    entity_id = _entity_id(hass, entry.entry_id, "button", key)
                    state = hass.states.get(entity_id)
                    assert state is not None
                    action = family.action_overrides[action_name]
                    if state.state == "unavailable":
                        continue
                    await hass.services.async_call(
                        "button",
                        "press",
                        {"entity_id": entity_id},
                        blocking=True,
                    )
                    assert fake.actions[-1] == (action["siid"], action["aiid"])
                    continue
                prop = _PROPERTY_BY_ENTITY.get(key, key.upper())
                assert prop in properties, (domain, key)
                assert properties[prop] in seen
        finally:
            assert await hass.config_entries.async_unload(entry.entry_id)
            await hass.async_block_till_done()
            release_device(device)
        assert_traffic_is_mapped(fake, family)


def _entry(version: int, device_name: str) -> MockConfigEntry:
    """Build a loopback config entry for one simulated vacuum."""
    return MockConfigEntry(
        domain=DOMAIN,
        unique_id=device_name,
        data={
            CONF_NAME: device_name,
            CONF_HOST: LOOPBACK_HOST,
            CONF_TOKEN: LOOPBACK_TOKEN,
            CONF_MAC: LOOPBACK_MAC,
            CONF_ACCOUNT_TYPE: "mi",
        },
        options={
            CONF_PREFER_CLOUD: False,
            CONF_NOTIFY: False,
            CONF_VERSION: version,
        },
    )


def _assert_registry(
    hass: HomeAssistant, entry_id: str, family: XiaomiModel, case: EntityCase
) -> None:
    """Assert the registry is exactly the Dreame entities plus this model's controls."""
    keys = _registry_keys(hass, entry_id)
    assert not any(domain == "time" for domain, _key in keys)
    expected = set(case.entities)
    expected.update((str(control.domain), control.key) for control in family.controls)
    assert keys == expected
    assert not any(domain == "camera" for domain, _key in keys)


def _registry_keys(hass: HomeAssistant, entry_id: str) -> set[tuple[str, str]]:
    """Return domain and unique-id suffix for every entity of one config entry."""
    registry = er.async_get(hass)
    keys: set[tuple[str, str]] = set()
    prefix = f"{LOOPBACK_MAC}_"
    for item in er.async_entries_for_config_entry(registry, entry_id):
        assert item.unique_id.startswith(prefix)
        keys.add((item.domain, item.unique_id.removeprefix(prefix)))
    return keys


def _entity_id(hass: HomeAssistant, entry_id: str, domain: str, key: str) -> str:
    """Return the entity id for one domain and unique-id suffix."""
    registry = er.async_get(hass)
    unique_id = f"{LOOPBACK_MAC}_{key}"
    for item in er.async_entries_for_config_entry(registry, entry_id):
        if item.domain == domain and item.unique_id == unique_id:
            return item.entity_id
    raise AssertionError((domain, key))


def _state(hass: HomeAssistant, entry_id: str, domain: str, key: str) -> str:
    """Return the state string of one entity."""
    state = hass.states.get(_entity_id(hass, entry_id, domain, key))
    assert state is not None
    return state.state


def _config_entry_id(hass: HomeAssistant) -> str:
    """Return the only loaded config entry id."""
    entry_ids = list(hass.data[DOMAIN])
    assert len(entry_ids) == 1
    return entry_ids[0]


async def _refresh(hass: HomeAssistant, entry_id: str) -> None:
    """Poll the device off the loop and publish the result."""
    coordinator = hass.data[DOMAIN][entry_id]
    await hass.async_add_executor_job(coordinator.device._request_properties)
    coordinator.async_set_updated_data()
    await hass.async_block_till_done()


async def _exercise_selects_switches_number_and_buttons(
    hass: HomeAssistant, fake: FakeMiio, family: XiaomiModel, case: EntityCase
) -> None:
    """Drive the legacy selects, switches, volume, and reset buttons."""
    entry_id = _config_entry_id(hass)
    await _select_legacy(hass, entry_id, case, "suction_level")
    await _select_legacy(hass, entry_id, case, "cleaning_mode")
    if "WATER_TANK" in family.property_overrides:
        tank = family.property_overrides["WATER_TANK"]
        fake.set_value(tank["siid"], tank["piid"], True)
        await _refresh(hass, entry_id)
    await _select_legacy(hass, entry_id, case, "water_volume")
    await _select_legacy(hass, entry_id, case, "cleaning_mode")
    if "AUTO_DUST_COLLECTING" in family.property_overrides:
        dust = family.property_overrides["AUTO_DUST_COLLECTING"]
        fake.set_value(dust["siid"], dust["piid"], 1)
        await _refresh(hass, entry_id)
        await _select_each(hass, entry_id, "auto_empty_frequency")
    present_switches = {key for domain, key in case.entities if domain == "switch"}
    for key in _LEGACY_SWITCHES:
        if key not in present_switches:
            continue
        if key == "dnd" and "DND" not in family.property_overrides:
            continue
        await _flip_legacy_switch(hass, entry_id, key)
    if ("number", "volume") in case.entities:
        await _set_volume_samples(hass, entry_id)
    await _press_reset_buttons(hass, entry_id, family, case)
    await _press_unavailable_auto_empty(hass, fake, entry_id, case)


async def _flip_legacy_switch(hass: HomeAssistant, entry_id: str, key: str) -> None:
    """Turn one legacy switch on and off."""
    entity_id = _entity_id(hass, entry_id, "switch", key)
    for service in ("turn_on", "turn_off"):
        await hass.services.async_call(
            "switch",
            service,
            {"entity_id": entity_id},
            blocking=True,
        )


async def _set_volume_samples(hass: HomeAssistant, entry_id: str) -> None:
    """Set volume to both ends and the midpoint."""
    volume_id = _entity_id(hass, entry_id, "number", "volume")
    for value in (0, 50, 100):
        await hass.services.async_call(
            "number",
            "set_value",
            {"entity_id": volume_id, "value": value},
            blocking=True,
        )


async def _press_reset_buttons(
    hass: HomeAssistant, entry_id: str, family: XiaomiModel, case: EntityCase
) -> None:
    """Press each legacy reset button this model exposes."""
    present = {key for domain, key in case.entities if domain == "button"}
    for key in _LEGACY_RESET_BUTTONS:
        if key not in present:
            continue
        if key.upper() not in family.action_overrides:
            continue
        await hass.services.async_call(
            "button",
            "press",
            {"entity_id": _entity_id(hass, entry_id, "button", key)},
            blocking=True,
        )


async def _press_unavailable_auto_empty(
    hass: HomeAssistant, fake: FakeMiio, entry_id: str, case: EntityCase
) -> None:
    """Assert a press sends nothing when this model exposes auto-empty."""
    if ("button", "start_auto_empty") not in case.entities:
        return
    empty_id = _entity_id(hass, entry_id, "button", "start_auto_empty")
    state = hass.states.get(empty_id)
    assert state is not None
    assert state.state == "unavailable"
    before = len(fake.actions)
    with contextlib.suppress(HomeAssistantError):
        await hass.services.async_call(
            "button",
            "press",
            {"entity_id": empty_id},
            blocking=True,
        )
    assert len(fake.actions) == before


async def _select_legacy(
    hass: HomeAssistant, entry_id: str, case: EntityCase, key: str
) -> None:
    """Select each option of a Dreame select this model still exposes."""
    if key in case.omitted_legacy_selects:
        return
    await _select_each(hass, entry_id, key)


async def _select_each(hass: HomeAssistant, entry_id: str, key: str) -> None:
    """Select every option of one select entity."""
    entity_id = _entity_id(hass, entry_id, "select", key)
    state = hass.states.get(entity_id)
    assert state is not None
    options = state.attributes["options"]
    assert options
    for option in options:
        await hass.services.async_call(
            "select",
            "select_option",
            {"entity_id": entity_id, "option": option},
            blocking=True,
        )


async def _exercise_vacuum_states(
    hass: HomeAssistant,
    entry_id: str,
    fake: FakeMiio,
    family: XiaomiModel,
    case: EntityCase,
) -> None:
    """Drive start, pause, resume, stop, return, locate, and the error states."""
    state = family.property_overrides["STATE"]
    charging = family.property_overrides.get("CHARGING_STATUS", {})
    error = family.property_overrides["ERROR"]
    vacuum_id = _entity_id(hass, entry_id, "vacuum", "dreame_vacuum")
    if not case.station_vacuum:
        await _exercise_sweep_vacuum(
            hass, fake, entry_id, family, vacuum_id, state, error
        )
        return
    await _show_vacuum(
        hass, fake, entry_id, vacuum_id, state, charging, error, 1, 2, 0, "idle"
    )
    await hass.services.async_call(
        "vacuum", "start", {"entity_id": vacuum_id}, blocking=True
    )
    await _refresh(hass, entry_id)
    assert _vacuum_state(hass, vacuum_id) == "cleaning"
    await hass.services.async_call(
        "vacuum", "pause", {"entity_id": vacuum_id}, blocking=True
    )
    await _refresh(hass, entry_id)
    assert _vacuum_state(hass, vacuum_id) == "paused"
    await hass.services.async_call(
        "vacuum", "start", {"entity_id": vacuum_id}, blocking=True
    )
    await _refresh(hass, entry_id)
    assert _vacuum_state(hass, vacuum_id) == "cleaning"
    assert fake.actions[-1] == (
        family.action_overrides["RESUME"]["siid"],
        family.action_overrides["RESUME"]["aiid"],
    )
    await hass.services.async_call(
        "vacuum", "stop", {"entity_id": vacuum_id}, blocking=True
    )
    assert fake.actions[-1] == (
        family.action_overrides["STOP"]["siid"],
        family.action_overrides["STOP"]["aiid"],
    )
    await _show_vacuum(
        hass, fake, entry_id, vacuum_id, state, charging, error, 6, 2, 0, "returning"
    )
    await hass.services.async_call(
        "vacuum", "return_to_base", {"entity_id": vacuum_id}, blocking=True
    )
    await _refresh(hass, entry_id)
    assert _vacuum_state(hass, vacuum_id) == "docked"
    await _show_vacuum(
        hass, fake, entry_id, vacuum_id, state, charging, error, 2, 1, 0, "docked"
    )
    # Released status lists can omit Error. The fault property below still sets it.
    error_status = [
        wire
        for wire, stored in family.state_by_wire.items()
        if stored == int(StoredState.ERROR)
    ]
    if error_status:
        await _show_vacuum(
            hass,
            fake,
            entry_id,
            vacuum_id,
            state,
            charging,
            error,
            min(error_status),
            2,
            0,
            "error",
        )
    await _show_vacuum(
        hass, fake, entry_id, vacuum_id, state, charging, error, 1, 2, 1, "error"
    )
    await hass.services.async_call(
        "vacuum", "locate", {"entity_id": vacuum_id}, blocking=True
    )
    assert fake.actions[-1] == (
        family.action_overrides["LOCATE"]["siid"],
        family.action_overrides["LOCATE"]["aiid"],
    )


async def _exercise_sweep_vacuum(
    hass: HomeAssistant,
    fake: FakeMiio,
    entry_id: str,
    family: XiaomiModel,
    vacuum_id: str,
    state: Mapping[str, int],
    error: Mapping[str, int],
) -> None:
    """Drive start, stop, return, and error without a charging property."""
    returning = wire_for_state(family, StoredState.RETURNING)
    charging = wire_for_state(family, StoredState.CHARGING)
    await _show_sweep(hass, fake, entry_id, vacuum_id, state, error, 1, 0, "idle")
    await hass.services.async_call(
        "vacuum", "start", {"entity_id": vacuum_id}, blocking=True
    )
    await _refresh(hass, entry_id)
    assert _vacuum_state(hass, vacuum_id) == "cleaning"
    if "PAUSE" in family.action_overrides:
        await hass.services.async_call(
            "vacuum", "pause", {"entity_id": vacuum_id}, blocking=True
        )
        await _refresh(hass, entry_id)
        assert _vacuum_state(hass, vacuum_id) == "paused"
        await hass.services.async_call(
            "vacuum", "start", {"entity_id": vacuum_id}, blocking=True
        )
        await _refresh(hass, entry_id)
        assert _vacuum_state(hass, vacuum_id) == "cleaning"
        assert fake.actions[-1] == (
            family.action_overrides["RESUME"]["siid"],
            family.action_overrides["RESUME"]["aiid"],
        )
    else:
        before = len(fake.actions)
        with contextlib.suppress(HomeAssistantError):
            await hass.services.async_call(
                "vacuum", "pause", {"entity_id": vacuum_id}, blocking=True
            )
        assert len(fake.actions) == before
        await _refresh(hass, entry_id)
        assert _vacuum_state(hass, vacuum_id) == "cleaning"
    await hass.services.async_call(
        "vacuum", "stop", {"entity_id": vacuum_id}, blocking=True
    )
    assert fake.actions[-1] == (
        family.action_overrides["STOP"]["siid"],
        family.action_overrides["STOP"]["aiid"],
    )
    await _show_sweep(
        hass, fake, entry_id, vacuum_id, state, error, returning, 0, "returning"
    )
    await hass.services.async_call(
        "vacuum", "return_to_base", {"entity_id": vacuum_id}, blocking=True
    )
    await _refresh(hass, entry_id)
    assert _vacuum_state(hass, vacuum_id) == "docked"
    await _show_sweep(
        hass, fake, entry_id, vacuum_id, state, error, charging, 0, "docked"
    )
    await _show_sweep(hass, fake, entry_id, vacuum_id, state, error, 1, 1, "error")
    if "LOCATE" in family.action_overrides:
        await hass.services.async_call(
            "vacuum", "locate", {"entity_id": vacuum_id}, blocking=True
        )
        assert fake.actions[-1] == (
            family.action_overrides["LOCATE"]["siid"],
            family.action_overrides["LOCATE"]["aiid"],
        )
        return
    before = len(fake.actions)
    with contextlib.suppress(HomeAssistantError):
        await hass.services.async_call(
            "vacuum", "locate", {"entity_id": vacuum_id}, blocking=True
        )
    assert len(fake.actions) == before


async def _show_sweep(
    hass: HomeAssistant,
    fake: FakeMiio,
    entry_id: str,
    vacuum_id: str,
    state: Mapping[str, int],
    error: Mapping[str, int],
    wire: int,
    error_wire: int,
    expected: str,
) -> None:
    """Publish one sweep status and assert the vacuum entity state."""
    fake.set_value(state["siid"], state["piid"], wire)
    fake.set_value(error["siid"], error["piid"], error_wire)
    await _refresh(hass, entry_id)
    assert _vacuum_state(hass, vacuum_id) == expected


def _vacuum_state(hass: HomeAssistant, vacuum_id: str) -> str:
    """Return the vacuum entity state."""
    state = hass.states.get(vacuum_id)
    assert state is not None
    return state.state


async def _show_vacuum(
    hass: HomeAssistant,
    fake: FakeMiio,
    entry_id: str,
    vacuum_id: str,
    state: Mapping[str, int],
    charging: Mapping[str, int],
    error: Mapping[str, int],
    wire: int,
    charging_wire: int,
    error_wire: int,
    expected: str,
) -> None:
    """Publish one status triple and assert the vacuum entity state."""
    fake.set_value(state["siid"], state["piid"], wire)
    fake.set_value(charging["siid"], charging["piid"], charging_wire)
    fake.set_value(error["siid"], error["piid"], error_wire)
    await _refresh(hass, entry_id)
    assert _vacuum_state(hass, vacuum_id) == expected


async def _exercise_sensors(
    hass: HomeAssistant,
    entry_id: str,
    fake: FakeMiio,
    family: XiaomiModel,
    case: EntityCase,
) -> None:
    """Assert every sensor key, then the counter, status, and firmware samples."""
    sensor_keys = {
        key for domain, key in _registry_keys(hass, entry_id) if domain == "sensor"
    }
    assert sensor_keys == {
        name.lower() for name in {**case.counter_samples, **case.status_samples}
    } | {"firmware_version"} | {
        control.key for control in family.controls if control.domain == "sensor"
    }
    await _show_sensors(hass, entry_id, fake, family, case.counter_samples)
    # Idle clears the current-job counters, so status is applied after them.
    await _show_sensors(hass, entry_id, fake, family, case.status_samples)
    # fw_ver "1.0_1" is stored as the integer after the underscore.
    firmware = _state(hass, entry_id, "sensor", "firmware_version")
    assert firmware == "1"


async def _show_sensors(
    hass: HomeAssistant,
    entry_id: str,
    fake: FakeMiio,
    family: XiaomiModel,
    samples: Mapping[str, tuple[object, str]],
) -> None:
    """Publish one sample per sensor and assert each state contains the text."""
    for name, (wire, _expected) in samples.items():
        mapping = family.property_overrides[name]
        fake.set_value(mapping["siid"], mapping["piid"], wire)
    await _refresh(hass, entry_id)
    for name, (_wire, expected) in samples.items():
        state = _state(hass, entry_id, "sensor", name.lower())
        assert expected in state, (name, state)


async def _exercise_binary_sensors(
    hass: HomeAssistant,
    entry_id: str,
    fake: FakeMiio,
    family: XiaomiModel,
    case: EntityCase,
) -> None:
    """Assert charging, problem, and maintenance, including one worn consumable."""
    binary_keys = {
        key
        for domain, key in _registry_keys(hass, entry_id)
        if domain == "binary_sensor"
    }
    expected_binary = {"problem", "maintenance"}
    if case.reports_charging:
        expected_binary.add("charging_state")
    assert binary_keys == expected_binary | {
        control.key for control in family.controls if control.domain == "binary_sensor"
    }
    battery = family.property_overrides["BATTERY_LEVEL"]
    error = family.property_overrides["ERROR"]
    fake.set_value(battery["siid"], battery["piid"], 90)
    if case.reports_charging:
        charging = family.property_overrides["CHARGING_STATUS"]
        fake.set_value(charging["siid"], charging["piid"], 1)
        await _refresh(hass, entry_id)
        assert _state(hass, entry_id, "binary_sensor", "charging_state") == "on"
        fake.set_value(charging["siid"], charging["piid"], 2)
        await _refresh(hass, entry_id)
        assert _state(hass, entry_id, "binary_sensor", "charging_state") == "off"
    fake.set_value(error["siid"], error["piid"], 0)
    await _refresh(hass, entry_id)
    assert _state(hass, entry_id, "binary_sensor", "problem") == "off"
    fake.set_value(error["siid"], error["piid"], 1)
    await _refresh(hass, entry_id)
    assert _state(hass, entry_id, "binary_sensor", "problem") == "on"
    for name in case.consumable_life:
        mapping = family.property_overrides[name]
        fake.set_value(mapping["siid"], mapping["piid"], 0)
    await _refresh(hass, entry_id)
    assert _state(hass, entry_id, "binary_sensor", "maintenance") == "on"
    for name in case.consumable_life:
        mapping = family.property_overrides[name]
        fake.set_value(mapping["siid"], mapping["piid"], 80)
    await _refresh(hass, entry_id)
    assert _state(hass, entry_id, "binary_sensor", "maintenance") == "off"
    worn = (
        "MAIN_BRUSH_LEFT"
        if "MAIN_BRUSH_LEFT" in family.property_overrides
        else case.consumable_life[0]
    )
    brush = family.property_overrides[worn]
    fake.set_value(brush["siid"], brush["piid"], 0)
    await _refresh(hass, entry_id)
    assert _state(hass, entry_id, "binary_sensor", "maintenance") == "on"


async def _exercise_controls(
    hass: HomeAssistant, entry_id: str, fake: FakeMiio, family: XiaomiModel
) -> None:
    """Drive every Xiaomi control in the domain it renders as."""
    for control in family.controls:
        await _exercise_one_control(hass, entry_id, fake, control)


async def _exercise_one_control(
    hass: HomeAssistant, entry_id: str, fake: FakeMiio, control: XiaomiControl
) -> None:
    """Drive one Xiaomi control through its Home Assistant service."""
    await _enable_control(hass, entry_id, control)
    if control.domain == "switch":
        await _flip_switch(hass, entry_id, control.key)
        return
    if control.domain == "select":
        await _seed_select(hass, entry_id, fake, control)
        await _select_each(hass, entry_id, control.key)
        return
    if control.domain == "number":
        await _set_number_samples(hass, entry_id, control)
        return
    if control.domain == "button":
        await hass.services.async_call(
            "button",
            "press",
            {"entity_id": _entity_id(hass, entry_id, "button", control.key)},
            blocking=True,
        )
        assert fake.actions[-1] == (control.siid, control.aiid)
        assert fake.action_inputs[-1] == [
            {"piid": piid, "value": value} for piid, value in control.action_parameters
        ]
        return
    if control.domain == "sensor":
        await _show_control_sensor(hass, entry_id, fake, control)
        return
    if control.domain == "binary_sensor":
        await _show_binary_control(hass, entry_id, fake, control)


async def _flip_switch(hass: HomeAssistant, entry_id: str, key: str) -> None:
    """Turn one switch on and off and assert both states."""
    entity_id = _entity_id(hass, entry_id, "switch", key)
    await hass.services.async_call(
        "switch", "turn_on", {"entity_id": entity_id}, blocking=True
    )
    assert _entity_state(hass, entity_id) == "on"
    await hass.services.async_call(
        "switch", "turn_off", {"entity_id": entity_id}, blocking=True
    )
    assert _entity_state(hass, entity_id) == "off"


def _entity_state(hass: HomeAssistant, entity_id: str) -> str:
    """Return one entity's state string."""
    state = hass.states.get(entity_id)
    assert state is not None
    return state.state


async def _enable_control(
    hass: HomeAssistant, entry_id: str, control: XiaomiControl
) -> None:
    """Enable a control that is off in the registry until the user turns it on."""
    if control.enabled_by_default:
        return
    registry = er.async_get(hass)
    entity_id = _entity_id(hass, entry_id, str(control.domain), control.key)
    current = registry.async_get(entity_id)
    if current is None or current.disabled_by is None:
        return
    registry.async_update_entity(entity_id, disabled_by=None)
    await hass.async_block_till_done()


async def _seed_select(
    hass: HomeAssistant, entry_id: str, fake: FakeMiio, control: XiaomiControl
) -> None:
    """Publish the first option so the select is not unavailable."""
    await _enable_control(hass, entry_id, control)
    if not control.readable:
        option = control.options[0][1]
        entity_id = _entity_id(hass, entry_id, "select", control.key)
        await hass.services.async_call(
            "select",
            "select_option",
            {"entity_id": entity_id, "option": option},
            blocking=True,
        )
        assert _entity_state(hass, entity_id) == option
        return
    value = control.options[0][0]
    if control.siid is not None:
        fake.set_value(control.siid, control.piid, value)
        await _refresh(hass, entry_id)
    state = hass.states.get(_entity_id(hass, entry_id, "select", control.key))
    assert state is not None
    assert state.state != "unavailable"


async def _set_number_samples(
    hass: HomeAssistant, entry_id: str, control: XiaomiControl
) -> None:
    """Set a number entity to its minimum, midpoint, and maximum."""
    entity_id = _entity_id(hass, entry_id, "number", control.key)
    assert control.minimum is not None
    assert control.maximum is not None
    middle = control.minimum + ((control.maximum - control.minimum) // 2)
    for value in (control.minimum, middle, control.maximum):
        await hass.services.async_call(
            "number",
            "set_value",
            {"entity_id": entity_id, "value": value},
            blocking=True,
        )
        assert _entity_state(hass, entity_id) == str(value)


async def _show_control_sensor(
    hass: HomeAssistant, entry_id: str, fake: FakeMiio, control: XiaomiControl
) -> None:
    """Publish each sensor sample and assert the entity state."""
    entity_id = _entity_id(hass, entry_id, "sensor", control.key)
    for wire, expected in _control_sensor_samples(control):
        fake.set_value(control.siid, control.piid, wire)
        await _refresh(hass, entry_id)
        assert _entity_state(hass, entity_id) == expected


def _control_sensor_samples(control: XiaomiControl) -> list[tuple[object, str]]:
    """Return the wire value and expected state for one control sensor."""
    if control.options:
        return [(value, slug) for value, slug in control.options]
    if control.value_kind == "string":
        return [("sample", "sample")]
    assert control.minimum is not None
    assert control.maximum is not None
    middle = control.minimum + ((control.maximum - control.minimum) // 2)
    return [(value, str(value)) for value in (control.minimum, middle, control.maximum)]


async def _show_binary_control(
    hass: HomeAssistant, entry_id: str, fake: FakeMiio, control: XiaomiControl
) -> None:
    """Publish both boolean wire forms and assert on and off."""
    entity_id = _entity_id(hass, entry_id, "binary_sensor", control.key)
    for wire, expected in ((0, "off"), (1, "on"), (False, "off"), (True, "on")):
        fake.set_value(control.siid, control.piid, wire)
        await _refresh(hass, entry_id)
        assert _entity_state(hass, entity_id) == expected

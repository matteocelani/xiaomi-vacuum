"""Home Assistant entities for xiaomi.vacuum.c104, the Mijia Sweep Mop 3."""

from __future__ import annotations

from typing import Final

from custom_components.dreame_vacuum.xiaomi import MODEL_MIJIA_SWEEP_MOP_3
import pytest
from tests.xiaomi.entity_contract import (
    EntityCase,
    assert_entities_read_or_write,
    exercise_home_assistant_entities,
)

from homeassistant.core import HomeAssistant

_ENTITIES: Final[frozenset[tuple[str, str]]] = frozenset(
    {
        ("binary_sensor", "maintenance"),
        ("binary_sensor", "problem"),
        ("button", "xiaomi_reset_filter"),
        ("button", "xiaomi_reset_main_brush"),
        ("button", "xiaomi_reset_mop"),
        ("button", "xiaomi_reset_side_brush"),
        ("button", "xiaomi_set_calibration"),
        ("button", "xiaomi_start_mop"),
        ("button", "xiaomi_start_only_sweep"),
        ("button", "xiaomi_start_sweep_mop"),
        ("number", "xiaomi_volume"),
        ("select", "xiaomi_ai_recognition"),
        ("select", "xiaomi_alarm"),
        ("select", "xiaomi_carpet_boost"),
        ("select", "xiaomi_dirt_recognition"),
        ("select", "xiaomi_mop_route"),
        ("select", "xiaomi_mop_shake"),
        ("select", "xiaomi_pet_recognition"),
        ("select", "xiaomi_repeat_clean"),
        ("select", "xiaomi_suction"),
        ("select", "xiaomi_sweep_mode"),
        ("select", "xiaomi_sweep_type"),
        ("select", "xiaomi_tank_shake"),
        ("select", "xiaomi_water_level"),
        ("sensor", "battery_level"),
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
        ("sensor", "side_brush_left"),
        ("sensor", "side_brush_time_left"),
        ("sensor", "state"),
        ("sensor", "xiaomi_dnd_enabled"),
        ("sensor", "xiaomi_dnd_end_hour"),
        ("sensor", "xiaomi_dnd_end_minute"),
        ("sensor", "xiaomi_dnd_start_hour"),
        ("sensor", "xiaomi_dnd_start_minute"),
        ("sensor", "xiaomi_dust_bin"),
        ("sensor", "xiaomi_mop_cloth"),
        ("vacuum", "dreame_vacuum"),
    }
)
_COUNTER_SAMPLES: Final[dict[str, tuple[object, str]]] = {
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
_STATUS_SAMPLES: Final[dict[str, tuple[object, str]]] = {
    "STATE": (1, "idle"),
}
_CONSUMABLE_LIFE: Final[tuple[str, ...]] = (
    "MAIN_BRUSH_LEFT",
    "SIDE_BRUSH_LEFT",
    "FILTER_LEFT",
    "MOP_PAD_LEFT",
)
_CASE = EntityCase(
    model=MODEL_MIJIA_SWEEP_MOP_3,
    device_name="Mijia Sweep Mop 3 Sim",
    entities=_ENTITIES,
    counter_samples=_COUNTER_SAMPLES,
    status_samples=_STATUS_SAMPLES,
    consumable_life=_CONSUMABLE_LIFE,
    omitted_legacy_selects=frozenset(
        {"cleaning_mode", "suction_level", "water_volume"}
    ),
    reports_charging=False,
    station_vacuum=False,
)

pytestmark = [
    pytest.mark.ha,
    pytest.mark.enable_socket,
    pytest.mark.allow_hosts(["127.0.0.1"]),
]


async def test_home_assistant_entities_follow_the_released_spec(
    hass: HomeAssistant,
    socket_enabled: None,
    enable_custom_integrations: None,
    integration_package: object,
) -> None:
    """Create every entity and drive every value the released spec allows."""
    del socket_enabled, enable_custom_integrations, integration_package
    await exercise_home_assistant_entities(hass, _CASE)


async def test_every_entity_reads_or_writes_a_mapped_wire(
    hass: HomeAssistant,
    socket_enabled: None,
    enable_custom_integrations: None,
    integration_package: object,
) -> None:
    """A created entity polls a mapped property or sends a mapped action or write."""
    del socket_enabled, enable_custom_integrations, integration_package
    await assert_entities_read_or_write(hass, _CASE)

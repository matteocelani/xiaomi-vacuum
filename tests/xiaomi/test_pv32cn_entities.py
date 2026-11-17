"""Home Assistant entities for xiaomi.vacuum.pv32cn, the Mijia Robot Vacuum 6."""

from __future__ import annotations

from typing import Final

from custom_components.xiaomi_robot_vacuum.xiaomi import MODEL_MIJIA_ROBOT_VACUUM_6
import pytest
from tests.xiaomi.entity_contract import (
    EntityCase,
    assert_entities_read_or_write,
    exercise_home_assistant_entities,
)

from homeassistant.core import HomeAssistant

_ENTITIES: Final[frozenset[tuple[str, str]]] = frozenset(
    {
        ("binary_sensor", "charging_state"),
        ("binary_sensor", "maintenance"),
        ("binary_sensor", "problem"),
        ("button", "reset_filter"),
        ("button", "reset_main_brush"),
        ("button", "reset_side_brush"),
        ("button", "start_auto_empty"),
        ("sensor", "firmware_version"),
        ("number", "volume"),
        ("select", "auto_empty_frequency"),
        ("select", "suction_level"),
        ("select", "water_volume"),
        ("sensor", "battery_level"),
        ("sensor", "charging_status"),
        ("sensor", "cleaned_area"),
        ("sensor", "cleaning_count"),
        ("sensor", "cleaning_time"),
        ("sensor", "error"),
        ("sensor", "filter_left"),
        ("sensor", "filter_time_left"),
        ("sensor", "main_brush_left"),
        ("sensor", "main_brush_time_left"),
        ("sensor", "relocation_status"),
        ("sensor", "side_brush_left"),
        ("sensor", "side_brush_time_left"),
        ("sensor", "state"),
        ("sensor", "task_status"),
        ("sensor", "total_cleaned_area"),
        ("sensor", "total_cleaning_time"),
        ("sensor", "water_tank"),
        ("switch", "auto_dust_collecting"),
        ("switch", "carpet_boost"),
        ("switch", "child_lock"),
        ("switch", "dnd"),
        ("switch", "resume_cleaning"),
        ("vacuum", "xiaomi_robot_vacuum"),
    }
)

_COUNTER_SAMPLES: Final[dict[str, tuple[object, str]]] = {
    "BATTERY_LEVEL": (55, "55"),
    "CLEANED_AREA": (12, "12"),
    "CLEANING_TIME": (9, "9"),
    "CLEANING_COUNT": (4, "4"),
    "TOTAL_CLEANED_AREA": (30, "30"),
    "TOTAL_CLEANING_TIME": (15, "15"),
    "MAIN_BRUSH_LEFT": (80, "80"),
    "MAIN_BRUSH_TIME_LEFT": (70, "70"),
    "SIDE_BRUSH_LEFT": (81, "81"),
    "SIDE_BRUSH_TIME_LEFT": (71, "71"),
    "FILTER_LEFT": (82, "82"),
    "FILTER_TIME_LEFT": (72, "72"),
    "ERROR": (0, "no_error"),
    "RELOCATION_STATUS": (False, "located"),
    "WATER_TANK": (True, "installed"),
}

_STATUS_SAMPLES: Final[dict[str, tuple[object, str]]] = {
    "CHARGING_STATUS": (2, "not_charging"),
    "STATE": (1, "idle"),
    "TASK_STATUS": (1, "completed"),
}

_CONSUMABLE_LIFE: Final[tuple[str, ...]] = (
    "MAIN_BRUSH_LEFT",
    "SIDE_BRUSH_LEFT",
    "FILTER_LEFT",
)

_CASE = EntityCase(
    model=MODEL_MIJIA_ROBOT_VACUUM_6,
    device_name="Mijia Robot Vacuum 6 Sim",
    entities=_ENTITIES,
    counter_samples=_COUNTER_SAMPLES,
    status_samples=_STATUS_SAMPLES,
    consumable_life=_CONSUMABLE_LIFE,
    omitted_legacy_selects=frozenset({"cleaning_mode"}),
)

pytestmark = [
    pytest.mark.ha,
    pytest.mark.enable_socket,
    pytest.mark.allow_hosts(["127.0.0.1"]),
]


async def test_home_assistant_entities_cover_every_exposed_control(
    hass: HomeAssistant,
    socket_enabled: None,
    enable_custom_integrations: None,
    integration_package: object,
) -> None:
    """Drive every entity this model creates and keep traffic on the map."""
    del socket_enabled, enable_custom_integrations, integration_package
    await exercise_home_assistant_entities(hass, _CASE)


async def test_every_entity_reads_or_writes_a_mapped_item(
    hass: HomeAssistant,
    socket_enabled: None,
    enable_custom_integrations: None,
    integration_package: object,
) -> None:
    """No entity is a no-op: each one polls a mapped property or sends a mapped wire."""
    del socket_enabled, enable_custom_integrations, integration_package
    await assert_entities_read_or_write(hass, _CASE)

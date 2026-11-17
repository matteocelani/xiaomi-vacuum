"""Home Assistant entities for xiaomi.vacuum.ov21gl, the Robot Vacuum 5 Pro."""

from __future__ import annotations

from typing import Final

from custom_components.xiaomi_robot_vacuum.xiaomi import MODEL_ROBOT_VACUUM_5_PRO
import pytest
from tests.xiaomi.entity_contract import EntityCase, exercise_home_assistant_entities

from homeassistant.core import HomeAssistant

_ENTITIES: Final[frozenset[tuple[str, str]]] = frozenset(
    {
        ("binary_sensor", "charging_state"),
        ("binary_sensor", "maintenance"),
        ("binary_sensor", "problem"),
        ("button", "reset_detergent"),
        ("button", "reset_filter"),
        ("button", "reset_main_brush"),
        ("button", "reset_mop_pad"),
        ("button", "reset_side_brush"),
        ("button", "start_auto_empty"),
        ("sensor", "firmware_version"),
        ("number", "volume"),
        ("select", "auto_empty_frequency"),
        ("select", "cleaning_mode"),
        ("select", "suction_level"),
        ("select", "water_volume"),
        ("sensor", "battery_level"),
        ("sensor", "charging_status"),
        ("sensor", "cleaned_area"),
        ("sensor", "detergent_left"),
        ("sensor", "detergent_time_left"),
        ("sensor", "cleaning_count"),
        ("sensor", "cleaning_time"),
        ("sensor", "error"),
        ("sensor", "filter_left"),
        ("sensor", "filter_time_left"),
        ("sensor", "main_brush_left"),
        ("sensor", "main_brush_time_left"),
        ("sensor", "mop_pad_left"),
        ("sensor", "mop_pad_time_left"),
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
    "DETERGENT_LEFT": (40, "40"),
    "DETERGENT_TIME_LEFT": (6, "6"),
    "TOTAL_CLEANED_AREA": (30, "30"),
    "TOTAL_CLEANING_TIME": (15, "15"),
    "MAIN_BRUSH_LEFT": (80, "80"),
    "MAIN_BRUSH_TIME_LEFT": (70, "70"),
    "SIDE_BRUSH_LEFT": (81, "81"),
    "SIDE_BRUSH_TIME_LEFT": (71, "71"),
    "FILTER_LEFT": (82, "82"),
    "FILTER_TIME_LEFT": (72, "72"),
    "MOP_PAD_LEFT": (83, "83"),
    "MOP_PAD_TIME_LEFT": (73, "73"),
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
    "MOP_PAD_LEFT",
    "DETERGENT_LEFT",
)

_CASE = EntityCase(
    model=MODEL_ROBOT_VACUUM_5_PRO,
    device_name="Vacuum 5 Pro Sim",
    entities=_ENTITIES,
    counter_samples=_COUNTER_SAMPLES,
    status_samples=_STATUS_SAMPLES,
    consumable_life=_CONSUMABLE_LIFE,
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

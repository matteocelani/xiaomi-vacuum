"""Home Assistant entities for xiaomi.vacuum.c108, the Xiaomi Robot Vacuum E5."""

from __future__ import annotations

from typing import Final

from custom_components.dreame_vacuum.xiaomi import MODEL_E5
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
        ("button", "reset_filter"),
        ("button", "reset_side_brush"),
        ("button", "xiaomi_start_charging"),
        ("button", "xiaomi_stop_charging"),
        ("select", "xiaomi_basic_suction"),
        ("select", "xiaomi_sweep_type"),
        ("sensor", "battery_level"),
        ("sensor", "cleaning_count"),
        ("sensor", "error"),
        ("sensor", "filter_left"),
        ("sensor", "firmware_version"),
        ("sensor", "side_brush_left"),
        ("sensor", "state"),
        ("sensor", "total_cleaning_time"),
        ("sensor", "xiaomi_charging_state"),
        ("sensor", "xiaomi_cleaning_area"),
        ("sensor", "xiaomi_cleaning_time"),
        ("sensor", "xiaomi_filter_minutes"),
        ("sensor", "xiaomi_last_clean_time"),
        ("sensor", "xiaomi_robot_notice"),
        ("sensor", "xiaomi_side_brush_minutes"),
        ("sensor", "xiaomi_total_clean_area"),
        ("switch", "xiaomi_light"),
        ("switch", "xiaomi_no_disturb"),
        ("switch", "xiaomi_sweep_break"),
        ("vacuum", "dreame_vacuum"),
    }
)
_COUNTER_SAMPLES: Final[dict[str, tuple[object, str]]] = {
    "BATTERY_LEVEL": (55, "55"),
    "CLEANING_COUNT": (7, "7"),
    "ERROR": (0, "e5_no_faults"),
    "FILTER_LEFT": (82, "82"),
    "SIDE_BRUSH_LEFT": (81, "81"),
    "TOTAL_CLEANING_TIME": (40, "40"),
}
_STATUS_SAMPLES: Final[dict[str, tuple[object, str]]] = {
    "STATE": (1, "idle"),
}
_CONSUMABLE_LIFE: Final[tuple[str, ...]] = (
    "FILTER_LEFT",
    "SIDE_BRUSH_LEFT",
)
_CASE = EntityCase(
    model=MODEL_E5,
    device_name="Robot Vacuum E5 Sim",
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


async def test_home_assistant_entities_follow_the_e5_spec(
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

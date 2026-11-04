"""Home Assistant entities for the Essential family."""

from __future__ import annotations

from typing import Final

from custom_components.dreame_vacuum.xiaomi import (
    MODEL_MIJIA_ESSENTIAL,
    MODEL_MIJIA_ESSENTIAL_V3,
    MODEL_MIJIA_G1,
)
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
        ("button", "reset_main_brush"),
        ("button", "reset_side_brush"),
        ("button", "xiaomi_start_charging"),
        ("button", "xiaomi_stop_charging"),
        ("number", "volume"),
        ("select", "xiaomi_fan_level"),
        ("select", "xiaomi_sweep_type"),
        ("select", "xiaomi_target_water"),
        ("select", "xiaomi_voice_language"),
        ("sensor", "battery_level"),
        ("sensor", "cleaning_count"),
        ("sensor", "cleaning_time"),
        ("sensor", "error"),
        ("sensor", "filter_left"),
        ("sensor", "firmware_version"),
        ("sensor", "main_brush_left"),
        ("sensor", "side_brush_left"),
        ("sensor", "state"),
        ("sensor", "xiaomi_charging_state"),
        ("sensor", "xiaomi_cleaning_area"),
        ("sensor", "xiaomi_filter_minutes"),
        ("sensor", "xiaomi_main_brush_minutes"),
        ("sensor", "xiaomi_side_brush_minutes"),
        ("sensor", "xiaomi_total_clean_area"),
        ("sensor", "xiaomi_total_clean_time"),
        ("switch", "dnd"),
        ("switch", "xiaomi_alarm_enabled"),
        ("vacuum", "dreame_vacuum"),
    }
)
_COUNTER_SAMPLES: Final[dict[str, tuple[object, str]]] = {
    "BATTERY_LEVEL": (55, "55"),
    "CLEANING_COUNT": (7, "7"),
    "CLEANING_TIME": (9, "9"),
    "FILTER_LEFT": (82, "82"),
    "MAIN_BRUSH_LEFT": (80, "80"),
    "SIDE_BRUSH_LEFT": (81, "81"),
}
_STATUS_SAMPLES: Final[dict[str, tuple[object, str]]] = {
    "STATE": (1, "idle"),
}
_CONSUMABLE_LIFE: Final[tuple[str, ...]] = (
    "FILTER_LEFT",
    "MAIN_BRUSH_LEFT",
    "SIDE_BRUSH_LEFT",
)
_MODELS = (
    (MODEL_MIJIA_G1, "Mijia G1 Sim"),
    (MODEL_MIJIA_ESSENTIAL, "Essential v2 Sim"),
    (MODEL_MIJIA_ESSENTIAL_V3, "Essential v3 Sim"),
)

pytestmark = [
    pytest.mark.ha,
    pytest.mark.enable_socket,
    pytest.mark.allow_hosts(["127.0.0.1"]),
]


def _case(model: str, device_name: str) -> EntityCase:
    """Entity case shared by the three released Essential models."""
    counters = dict(_COUNTER_SAMPLES)
    if model == MODEL_MIJIA_G1:
        counters["ERROR"] = (0, "essential_everything_ok")
    else:
        counters["ERROR"] = (0, "essential_no_faults")
    return EntityCase(
        model=model,
        device_name=device_name,
        entities=_ENTITIES,
        counter_samples=counters,
        status_samples=_STATUS_SAMPLES,
        consumable_life=_CONSUMABLE_LIFE,
        omitted_legacy_selects=frozenset(
            {"cleaning_mode", "suction_level", "water_volume"}
        ),
        reports_charging=False,
        station_vacuum=False,
    )


@pytest.mark.parametrize(("model", "device_name"), _MODELS, ids=("v1", "v2", "v3"))
async def test_home_assistant_entities_follow_the_essential_spec(
    hass: HomeAssistant,
    socket_enabled: None,
    enable_custom_integrations: None,
    integration_package: object,
    model: str,
    device_name: str,
) -> None:
    """Create every entity and drive every value the released spec allows."""
    del socket_enabled, enable_custom_integrations, integration_package
    await exercise_home_assistant_entities(hass, _case(model, device_name))


@pytest.mark.parametrize(("model", "device_name"), _MODELS, ids=("v1", "v2", "v3"))
async def test_every_entity_reads_or_writes_a_mapped_wire(
    hass: HomeAssistant,
    socket_enabled: None,
    enable_custom_integrations: None,
    integration_package: object,
    model: str,
    device_name: str,
) -> None:
    """A created entity polls a mapped property or sends a mapped action or write."""
    del socket_enabled, enable_custom_integrations, integration_package
    await assert_entities_read_or_write(hass, _case(model, device_name))

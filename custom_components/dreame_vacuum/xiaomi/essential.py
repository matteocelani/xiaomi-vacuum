"""Essential spec family shared by mijia.vacuum.v1, v2, and v3."""

from __future__ import annotations

from enum import IntEnum
from typing import Final

from .controls import (
    XiaomiControl,
    action_button,
    boolean_switch,
    enum_select,
    enum_sensor,
    measurement,
)
from .model import StoredState, wire_map

_UINT16_MAX: Final = 65535
_UINT32_MAX: Final = 4294967295
_FILTER_MINUTES_MAX: Final = 18000
_MAIN_BRUSH_MINUTES_MAX: Final = 18000
_SIDE_BRUSH_MINUTES_MAX: Final = 9000
_MINUTES: Final = "min"

_SWEEP_TYPE_OPTIONS: Final[tuple[tuple[int, str], ...]] = (
    (1, "global"),
    (2, "point"),
    (3, "edge"),
)
_WATER_OPTIONS: Final[tuple[tuple[int, str], ...]] = (
    (1, "level1"),
    (2, "level2"),
    (3, "level3"),
)
_FAN_OPTIONS: Final[tuple[tuple[int, str], ...]] = (
    (0, "silent"),
    (1, "standard"),
    (2, "medium"),
    (3, "strong"),
)
_CHARGING_OPTIONS: Final[tuple[tuple[int, str], ...]] = (
    (0, "not_charging"),
    (1, "charging"),
    (2, "charging_finished"),
)
_LANGUAGE_OPTIONS: Final[tuple[tuple[int, str], ...]] = (
    (0, "simplified_chinese"),
    (1, "english"),
)


class EssentialWireState(IntEnum):
    """Status codes published by the released Essential spec."""

    IDLE = 1
    SWEEPING = 2
    PAUSED = 3
    ERROR = 4
    CHARGING = 5
    RETURNING = 6


ESSENTIAL_PROPERTIES: Final[dict[str, dict[str, int]]] = {
    "STATE": {"siid": 2, "piid": 1},
    "ERROR": {"siid": 2, "piid": 2},
    "BATTERY_LEVEL": {"siid": 3, "piid": 1},
    "VOLUME": {"siid": 4, "piid": 2},
    "FILTER_LEFT": {"siid": 11, "piid": 1},
    "MAIN_BRUSH_LEFT": {"siid": 14, "piid": 1},
    "SIDE_BRUSH_LEFT": {"siid": 15, "piid": 1},
    "CLEANING_TIME": {"siid": 9, "piid": 2},
    "CLEANING_COUNT": {"siid": 9, "piid": 5},
    "DND": {"siid": 12, "piid": 2},
}
ESSENTIAL_ACTIONS: Final[dict[str, dict[str, int]]] = {
    "START": {"siid": 2, "aiid": 1},
    "STOP": {"siid": 2, "aiid": 2},
    "CHARGE": {"siid": 2, "aiid": 3},
    "LOCATE": {"siid": 6, "aiid": 1},
    "RESET_FILTER": {"siid": 11, "aiid": 1},
    "RESET_MAIN_BRUSH": {"siid": 14, "aiid": 1},
    "RESET_SIDE_BRUSH": {"siid": 15, "aiid": 1},
}
ESSENTIAL_STATES: Final[dict[int, int]] = wire_map(
    (
        (EssentialWireState.IDLE, StoredState.IDLE),
        (EssentialWireState.SWEEPING, StoredState.SWEEPING),
        (EssentialWireState.PAUSED, StoredState.PAUSED),
        (EssentialWireState.ERROR, StoredState.ERROR),
        (EssentialWireState.CHARGING, StoredState.CHARGING),
        (EssentialWireState.RETURNING, StoredState.RETURNING),
    )
)
# Charging wire 0 means not charging, so it is not the Dreame charging property.
ESSENTIAL_CONTROLS: Final[tuple[XiaomiControl, ...]] = (
    enum_select("xiaomi_sweep_type", 2, 4, _SWEEP_TYPE_OPTIONS),
    enum_select("xiaomi_target_water", 2, 5, _WATER_OPTIONS),
    enum_select("xiaomi_fan_level", 2, 6, _FAN_OPTIONS),
    enum_sensor("xiaomi_charging_state", 3, 2, _CHARGING_OPTIONS),
    boolean_switch("xiaomi_alarm_enabled", 4, 1),
    measurement("xiaomi_filter_minutes", 11, 2, 0, _FILTER_MINUTES_MAX, _MINUTES),
    measurement(
        "xiaomi_main_brush_minutes", 14, 2, 0, _MAIN_BRUSH_MINUTES_MAX, _MINUTES
    ),
    measurement(
        "xiaomi_side_brush_minutes", 15, 2, 0, _SIDE_BRUSH_MINUTES_MAX, _MINUTES
    ),
    measurement("xiaomi_cleaning_area", 9, 1, 0, _UINT16_MAX),
    measurement("xiaomi_total_clean_area", 9, 3, 0, _UINT32_MAX),
    measurement("xiaomi_total_clean_time", 9, 4, 0, _UINT32_MAX),
    enum_select("xiaomi_voice_language", 12, 1, _LANGUAGE_OPTIONS),
    action_button("xiaomi_start_charging", 13, 1),
    action_button("xiaomi_stop_charging", 13, 2),
)

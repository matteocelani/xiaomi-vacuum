"""Sweep-service spec family shared by E10-class Xiaomi vacuums."""

from __future__ import annotations

from enum import IntEnum
from typing import Final

from .controls import (
    XiaomiControl,
    action_button,
    enum_select,
    enum_sensor,
    measurement,
    number_control,
    uint8_switch,
    write_only_number,
    write_only_select,
)
from .model import StoredState, wire_map

_CLEANING_MODE_OPTIONS: Final[tuple[tuple[int, str], ...]] = (
    (0, "sweep"),
    (1, "sweep_and_mop"),
    (2, "mop"),
)


class SweepWireState(IntEnum):
    """Status codes published by the E10 sweep spec."""

    SLEEP = 0
    IDLE = 1
    PAUSED = 2
    RETURNING = 3
    CHARGING = 4
    SWEEPING = 5
    SWEEPING_AND_MOPPING = 6
    MOPPING = 7
    UPGRADING = 8


_ALARM_OPTIONS: Final[tuple[tuple[int, str], ...]] = ((1, "play"),)
_SWEEP_TYPE_OPTIONS: Final[tuple[tuple[int, str], ...]] = (
    (0, "global"),
    (2, "edge"),
    (4, "point"),
    (5, "remote"),
)
_REPEAT_OPTIONS: Final[tuple[tuple[int, str], ...]] = ((0, "close"),)
_BOX_OPTIONS: Final[tuple[tuple[int, str], ...]] = (
    (0, "none"),
    (1, "dust_box"),
    (2, "water_box"),
    (3, "two_in_one"),
)
_CLOTH_OPTIONS: Final[tuple[tuple[int, str], ...]] = (
    (0, "none"),
    (1, "exist"),
)
_SUCTION_OPTIONS: Final[tuple[tuple[int, str], ...]] = (
    (0, "close"),
    (1, "one"),
    (2, "two"),
    (3, "three"),
    (4, "forth"),
)
_WATER_OPTIONS: Final[tuple[tuple[int, str], ...]] = (
    (0, "close"),
    (1, "one"),
    (2, "two"),
    (3, "three"),
)
_MOP_ROUTE_OPTIONS: Final[tuple[tuple[int, str], ...]] = ((0, "bowtype"),)
_DND_OPTIONS: Final[tuple[tuple[int, str], ...]] = (
    (0, "close"),
    (1, "open"),
)

SWEEP_PROPERTIES: Final[dict[str, dict[str, int]]] = {
    "STATE": {"siid": 2, "piid": 1},
    "ERROR": {"siid": 2, "piid": 2},
    "BATTERY_LEVEL": {"siid": 3, "piid": 1},
    "SIDE_BRUSH_LEFT": {"siid": 7, "piid": 8},
    "SIDE_BRUSH_TIME_LEFT": {"siid": 7, "piid": 9},
    "MAIN_BRUSH_LEFT": {"siid": 7, "piid": 10},
    "MAIN_BRUSH_TIME_LEFT": {"siid": 7, "piid": 11},
    "FILTER_LEFT": {"siid": 7, "piid": 12},
    "FILTER_TIME_LEFT": {"siid": 7, "piid": 13},
    "MOP_PAD_LEFT": {"siid": 7, "piid": 14},
    "MOP_PAD_TIME_LEFT": {"siid": 7, "piid": 15},
    "CLEANING_TIME": {"siid": 7, "piid": 22},
    "CLEANED_AREA": {"siid": 7, "piid": 23},
}
SWEEP_ACTIONS: Final[dict[str, dict[str, int]]] = {
    "START": {"siid": 2, "aiid": 1},
    "STOP": {"siid": 2, "aiid": 2},
    "CHARGE": {"siid": 3, "aiid": 1},
}
# Later models add wires with compose_codes. S12 swaps wires 6 and 7.
SWEEP_STATES: Final[dict[int, int]] = wire_map(
    (
        (SweepWireState.SLEEP, StoredState.IDLE),
        (SweepWireState.IDLE, StoredState.IDLE),
        (SweepWireState.PAUSED, StoredState.PAUSED),
        (SweepWireState.RETURNING, StoredState.RETURNING),
        (SweepWireState.CHARGING, StoredState.CHARGING),
        (SweepWireState.SWEEPING, StoredState.SWEEPING),
        (SweepWireState.SWEEPING_AND_MOPPING, StoredState.SWEEPING_AND_MOPPING),
        (SweepWireState.MOPPING, StoredState.MOPPING),
        (SweepWireState.UPGRADING, StoredState.UPGRADING),
    )
)
SWEEP_CONTROLS: Final[tuple[XiaomiControl, ...]] = (
    enum_select("xiaomi_sweep_mode", 2, 4, _CLEANING_MODE_OPTIONS),
    enum_select("xiaomi_alarm", 4, 1, _ALARM_OPTIONS),
    number_control("xiaomi_volume", 4, 2, 0, 10),
    enum_select("xiaomi_sweep_type", 2, 8, _SWEEP_TYPE_OPTIONS),
    enum_select("xiaomi_repeat_clean", 7, 1, _REPEAT_OPTIONS),
    enum_sensor("xiaomi_dust_bin", 7, 3, _BOX_OPTIONS),
    enum_sensor("xiaomi_mop_cloth", 7, 4, _CLOTH_OPTIONS),
    enum_select("xiaomi_suction", 7, 5, _SUCTION_OPTIONS),
    enum_select("xiaomi_water_level", 7, 6, _WATER_OPTIONS),
    enum_select("xiaomi_mop_route", 7, 7, _MOP_ROUTE_OPTIONS),
    enum_sensor("xiaomi_dnd_enabled", 12, 1, _DND_OPTIONS),
    measurement("xiaomi_dnd_start_hour", 12, 2, 0, 23, "h"),
    measurement("xiaomi_dnd_start_minute", 12, 3, 0, 59, "min"),
    measurement("xiaomi_dnd_end_hour", 12, 4, 0, 23, "h"),
    measurement("xiaomi_dnd_end_minute", 12, 5, 0, 59, "min"),
    action_button("xiaomi_start_only_sweep", 2, 3),
    action_button("xiaomi_start_sweep_mop", 2, 5),
    action_button("xiaomi_start_mop", 2, 6),
    action_button("xiaomi_set_calibration", 7, 2),
    # reset-consumable takes property 17. 1 middle, 2 side, 4 filter, 8 cloth.
    action_button("xiaomi_reset_main_brush", 7, 1, ((17, 1),)),
    action_button("xiaomi_reset_side_brush", 7, 1, ((17, 2),)),
    action_button("xiaomi_reset_filter", 7, 1, ((17, 4),)),
    action_button("xiaomi_reset_mop", 7, 1, ((17, 8),)),
)

_CLOSE_OPEN: Final[tuple[tuple[int, str], ...]] = ((0, "close"), (1, "open"))

# Write-only sweep settings. Models that do not publish a key must not receive it.
CARPET_AVOID: Final = write_only_select("xiaomi_carpet_avoid", 7, 47, _CLOSE_OPEN)
SWEEP_AVOID: Final = write_only_select("xiaomi_sweep_avoid", 7, 57, _CLOSE_OPEN)
MOP_AVOID: Final = write_only_select("xiaomi_mop_avoid", 7, 58, _CLOSE_OPEN)
BACK_WASH_AREA: Final = write_only_select(
    "xiaomi_back_wash_area",
    7,
    62,
    ((5, "five"), (10, "ten")),
)
DRY_TIME: Final = write_only_number("xiaomi_dry_time", 7, 63, 4, 12, unit="h")
REMEMBER_MAP: Final = uint8_switch(
    "xiaomi_remember_map",
    10,
    1,
    _CLOSE_OPEN,
)

"""Xiaomi Robot Vacuum E5 record on its own MIoT layout."""

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
    text_sensor,
)
from .model import MODEL_E5, StoredState, XiaomiModel, wire_map

_UINT32_MAX: Final = 4294967295
_CONSUMABLE_MINUTES_MAX: Final = 18000
_AREA_UNIT: Final = "0.01 m²"
_SECONDS: Final = "s"
_MINUTES: Final = "min"

_SUCTION_OPTIONS: Final[tuple[tuple[int, str], ...]] = (
    (0, "silent"),
    (1, "basic"),
    (2, "strong"),
)
_SWEEP_TYPE_OPTIONS: Final[tuple[tuple[int, str], ...]] = (
    (1, "global"),
    (2, "point"),
    (3, "edge"),
)
_CHARGING_OPTIONS: Final[tuple[tuple[int, str], ...]] = (
    (1, "not_charging"),
    (2, "charging"),
    (3, "charging_finished"),
)
_NOTICE_OPTIONS: Final[tuple[tuple[int, str], ...]] = (
    (0, "none"),
    (1, "schedule_cleaning"),
    (2, "keep_cleaning"),
    (3, "start_recharging"),
    (4, "stop_recharging"),
    (5, "battery_20"),
    (6, "cleaning_complete"),
    (7, "upgrade_failed"),
    (8, "update_succeeded"),
    (9, "dnd_blocks_resume"),
    (10, "dnd_blocks_schedule"),
    (11, "busy_blocks_schedule"),
    (12, "shutdown"),
    (13, "filter_life"),
    (14, "side_brush_life"),
)


class _WireState(IntEnum):
    """Status codes published by the released E5 spec."""

    IDLE = 1
    SWEEPING = 2
    PAUSED = 3
    ERROR = 4
    CHARGING = 5
    RETURNING = 6
    CHARGING_COMPLETED = 7


class _WireFault(IntEnum):
    """Fault codes published by the released E5 spec, which are not Dreame codes."""

    NO_FAULTS = 0
    LEFT_WHEEL_STUCK = 1
    RIGHT_WHEEL_STUCK = 2
    FRONT_BUMPER_STUCK = 3
    SIDE_BRUSH_STUCK = 4
    ANTI_DROP_SENSOR = 5
    WHEEL_SUSPENDED = 6
    FAN_ERROR = 7
    BATTERY_LOW = 8
    CHARGING_ERROR = 9
    MACHINE_TRAPPED = 10
    LEFT_WHEEL_ERROR = 11
    RIGHT_WHEEL_ERROR = 12
    SIDE_BRUSH_ERROR = 13
    BATTERY_ERROR = 14
    GROUND_SLOPE = 15


_FAULT_NAMES: Final[dict[int, str]] = {
    int(_WireFault.NO_FAULTS): "e5_no_faults",
    int(_WireFault.LEFT_WHEEL_STUCK): "e5_left_wheel_stuck",
    int(_WireFault.RIGHT_WHEEL_STUCK): "e5_right_wheel_stuck",
    int(_WireFault.FRONT_BUMPER_STUCK): "e5_front_bumper_stuck",
    int(_WireFault.SIDE_BRUSH_STUCK): "e5_side_brush_stuck",
    int(_WireFault.ANTI_DROP_SENSOR): "e5_anti_drop_sensor",
    int(_WireFault.WHEEL_SUSPENDED): "e5_wheel_suspended",
    int(_WireFault.FAN_ERROR): "e5_fan_error",
    int(_WireFault.BATTERY_LOW): "e5_battery_low",
    int(_WireFault.CHARGING_ERROR): "e5_charging_error",
    int(_WireFault.MACHINE_TRAPPED): "e5_machine_trapped",
    int(_WireFault.LEFT_WHEEL_ERROR): "e5_left_wheel_error",
    int(_WireFault.RIGHT_WHEEL_ERROR): "e5_right_wheel_error",
    int(_WireFault.SIDE_BRUSH_ERROR): "e5_side_brush_error",
    int(_WireFault.BATTERY_ERROR): "e5_battery_error",
    int(_WireFault.GROUND_SLOPE): "e5_ground_slope",
}


_PROPERTIES: Final[dict[str, dict[str, int]]] = {
    "STATE": {"siid": 2, "piid": 1},
    "ERROR": {"siid": 2, "piid": 2},
    "BATTERY_LEVEL": {"siid": 3, "piid": 1},
    "FILTER_LEFT": {"siid": 6, "piid": 1},
    "SIDE_BRUSH_LEFT": {"siid": 7, "piid": 1},
    "TOTAL_CLEANING_TIME": {"siid": 9, "piid": 2},
    "CLEANING_COUNT": {"siid": 9, "piid": 3},
}
_ACTIONS: Final[dict[str, dict[str, int]]] = {
    "START": {"siid": 2, "aiid": 1},
    "STOP": {"siid": 2, "aiid": 2},
    "PAUSE": {"siid": 2, "aiid": 3},
    "RESUME": {"siid": 2, "aiid": 4},
    "CHARGE": {"siid": 2, "aiid": 8},
    "LOCATE": {"siid": 4, "aiid": 1},
    "RESET_FILTER": {"siid": 6, "aiid": 1},
    "RESET_SIDE_BRUSH": {"siid": 7, "aiid": 1},
}
_STATES: Final[dict[int, int]] = wire_map(
    (
        (_WireState.IDLE, StoredState.IDLE),
        (_WireState.SWEEPING, StoredState.SWEEPING),
        (_WireState.PAUSED, StoredState.PAUSED),
        (_WireState.ERROR, StoredState.ERROR),
        (_WireState.CHARGING, StoredState.CHARGING),
        (_WireState.RETURNING, StoredState.RETURNING),
        (_WireState.CHARGING_COMPLETED, StoredState.CHARGING_COMPLETED),
    )
)
# Released c108 status and sweep-type lists do not match the sweep or station profiles.
_CONTROLS: Final[tuple[XiaomiControl, ...]] = (
    enum_select("xiaomi_sweep_type", 2, 4, _SWEEP_TYPE_OPTIONS),
    enum_select("xiaomi_basic_suction", 2, 5, _SUCTION_OPTIONS),
    measurement("xiaomi_cleaning_area", 2, 6, 0, _UINT32_MAX, _AREA_UNIT),
    measurement("xiaomi_cleaning_time", 2, 7, 0, _UINT32_MAX, _SECONDS),
    text_sensor("xiaomi_last_clean_time", 2, 9),
    boolean_switch("xiaomi_sweep_break", 2, 12),
    enum_sensor("xiaomi_charging_state", 3, 2, _CHARGING_OPTIONS),
    measurement("xiaomi_filter_minutes", 6, 2, 0, _CONSUMABLE_MINUTES_MAX, _MINUTES),
    measurement(
        "xiaomi_side_brush_minutes", 7, 2, 0, _CONSUMABLE_MINUTES_MAX, _MINUTES
    ),
    boolean_switch("xiaomi_no_disturb", 10, 1),
    measurement("xiaomi_total_clean_area", 9, 1, 0, _UINT32_MAX),
    enum_sensor("xiaomi_robot_notice", 12, 1, _NOTICE_OPTIONS),
    boolean_switch("xiaomi_light", 14, 1),
    action_button("xiaomi_start_charging", 11, 1),
    action_button("xiaomi_stop_charging", 11, 2),
)

E5: Final = XiaomiModel(
    model=MODEL_E5,
    property_overrides=_PROPERTIES,
    action_overrides=_ACTIONS,
    state_by_wire=_STATES,
    task_by_wire={},
    controls=_CONTROLS,
    fault_names=_FAULT_NAMES,
)

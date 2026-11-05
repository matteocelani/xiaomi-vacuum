"""Xiaomi S20+ model record on its own siid layout."""

from __future__ import annotations

from enum import IntEnum
from typing import Final

from .model import MODEL_S20_PLUS, XiaomiModel
from .profile import StoredState, StoredTask, wire_map


class _WireState(IntEnum):
    """Wire status codes for xiaomi.vacuum.b108gl."""

    IDLE = 1
    CHARGING = 2
    BREAK_CHARGING = 3
    SWEEPING = 4
    PAUSED = 5
    RETURNING = 6
    REMOTE = 7
    CHARGED = 8
    MAPPING = 9
    UPDATING = 10


class _WireTask(IntEnum):
    """Wire sweep-type codes for xiaomi.vacuum.b108gl."""

    GLOBAL = 1
    AREA = 4
    MAPPING = 5
    GO_CHARGING = 6
    REMOTE = 7
    SELECT_ROOM = 8
    CUSTOM = 9


_PROPERTIES: Final[dict[str, dict[str, int]]] = {
    "STATE": {"siid": 2, "piid": 1},
    "ERROR": {"siid": 2, "piid": 2},
    "CLEANING_MODE": {"siid": 2, "piid": 3},
    "TASK_STATUS": {"siid": 2, "piid": 4},
    "CLEANED_AREA": {"siid": 2, "piid": 5},
    "CLEANING_TIME": {"siid": 2, "piid": 6},
    "SUCTION_LEVEL": {"siid": 2, "piid": 8},
    "WATER_VOLUME": {"siid": 2, "piid": 9},
    "CARPET_CLEANING": {"siid": 2, "piid": 20},
    "BATTERY_LEVEL": {"siid": 3, "piid": 1},
    "CHARGING_STATUS": {"siid": 3, "piid": 2},
    "VOLUME": {"siid": 4, "piid": 2},
    "CHILD_LOCK": {"siid": 5, "piid": 1},
    "WATER_TANK": {"siid": 6, "piid": 1},
    "DND": {"siid": 6, "piid": 3},
    "SCHEDULE": {"siid": 6, "piid": 5},
    "CARPET_BOOST": {"siid": 6, "piid": 6},
    "RELOCATION_STATUS": {"siid": 6, "piid": 9},
    "RESUME_CLEANING": {"siid": 6, "piid": 11},
    "FAULTS": {"siid": 6, "piid": 13},
    "MAIN_BRUSH_TIME_LEFT": {"siid": 8, "piid": 1},
    "MAIN_BRUSH_LEFT": {"siid": 8, "piid": 2},
    "SIDE_BRUSH_TIME_LEFT": {"siid": 9, "piid": 1},
    "SIDE_BRUSH_LEFT": {"siid": 9, "piid": 2},
    "FILTER_TIME_LEFT": {"siid": 10, "piid": 1},
    "FILTER_LEFT": {"siid": 10, "piid": 2},
    "MOP_PAD_TIME_LEFT": {"siid": 11, "piid": 1},
    "MOP_PAD_LEFT": {"siid": 11, "piid": 2},
}

_ACTIONS: Final[dict[str, dict[str, int]]] = {
    "START": {"siid": 2, "aiid": 1},
    "STOP": {"siid": 2, "aiid": 2},
    "PAUSE": {"siid": 2, "aiid": 6},
    "RESUME": {"siid": 6, "aiid": 1},
    "CHARGE": {"siid": 3, "aiid": 1},
    "LOCATE": {"siid": 6, "aiid": 6},
    "RESET_MAIN_BRUSH": {"siid": 8, "aiid": 1},
    "RESET_SIDE_BRUSH": {"siid": 9, "aiid": 1},
    "RESET_FILTER": {"siid": 10, "aiid": 1},
    "RESET_MOP_PAD": {"siid": 11, "aiid": 1},
}

_STATES: Final[dict[int, int]] = wire_map(
    (
        (_WireState.IDLE, StoredState.IDLE),
        (_WireState.CHARGING, StoredState.CHARGING),
        (_WireState.BREAK_CHARGING, StoredState.CHARGING),
        (_WireState.SWEEPING, StoredState.SWEEPING),
        (_WireState.PAUSED, StoredState.PAUSED),
        (_WireState.RETURNING, StoredState.RETURNING),
        (_WireState.REMOTE, StoredState.REMOTE_CONTROL),
        (_WireState.CHARGED, StoredState.CHARGING_COMPLETED),
        (_WireState.MAPPING, StoredState.BUILDING),
        (_WireState.UPDATING, StoredState.UPGRADING),
    )
)

_TASKS: Final[dict[int, int]] = wire_map(
    (
        (_WireTask.GLOBAL, StoredTask.AUTO_CLEANING),
        (_WireTask.AREA, StoredTask.ZONE_CLEANING),
        (_WireTask.MAPPING, StoredTask.FAST_MAPPING),
        (_WireTask.GO_CHARGING, StoredTask.COMPLETED),
        (_WireTask.REMOTE, StoredTask.COMPLETED),
        (_WireTask.SELECT_ROOM, StoredTask.SEGMENT_CLEANING),
        (_WireTask.CUSTOM, StoredTask.SPOT_CLEANING),
    )
)

S20_PLUS: Final = XiaomiModel(
    model=MODEL_S20_PLUS,
    property_overrides=_PROPERTIES,
    action_overrides=_ACTIONS,
    state_by_wire=_STATES,
    task_by_wire=_TASKS,
)

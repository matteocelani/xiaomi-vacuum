"""Shared station addresses for X20 Max-like Xiaomi models."""

from __future__ import annotations

from enum import IntEnum
from typing import Final

from .model import (
    StoredState,
    StoredTask,
    compose_addresses,
    compose_codes,
    wire_map,
)


class StationWireState(IntEnum):
    """Wire status codes shared by the X20 Max station spec."""

    IDLE = 1
    CHARGING = 2
    BREAK_CHARGING = 3
    SWEEPING = 4
    PAUSED = 5
    RETURNING = 6
    GO_WASH = 7
    REMOTE = 8
    CHARGED = 9
    BUILDING = 10
    UPDATING = 11
    MULTI_TASK_STATION = 12
    MULTI_TASK_RECHARGE = 13
    STATION_WORKING = 14
    ERROR = 15
    SWEEPING_AND_MOPPING = 16
    MOPPING = 17
    MAPPING_PAUSE = 18
    GO_CHARGE_BREAK = 19
    WASH_BREAK = 20
    GO_CHARGE_BUILDING = 21


class StationWireTask(IntEnum):
    """Wire sweep-type codes shared by the X20 Max station spec."""

    GLOBAL = 1
    ZONE = 2
    AREA = 3
    EDGE = 4
    CUSTOM = 5
    POINT = 6
    CUSTOM_AREA = 7


class ExtendedStationWireState(IntEnum):
    """Status codes the extended station spec adds after the X20 Max list."""

    STATION_ASSISTING = 22
    STATION_ASSISTED = 23
    RETURNING_DURING_ASSIST = 24


class SummonWireState(IntEnum):
    """Status codes the summon specs add after the extended station list."""

    SELF_CHECK = 25
    SUMMONING = 26
    SWEEP_SUMMONING = 27


class ExtendedStationWireTask(IntEnum):
    """Sweep-type codes the extended station spec adds after the X20 Max list."""

    APPOINTMENT = 8
    LINKAGE = 9
    FAST_MAPPING = 10
    AI_HOSTING = 11


STATION_PROPERTIES: Final[dict[str, dict[str, int]]] = {
    "STATE": {"siid": 2, "piid": 2},
    "ERROR": {"siid": 2, "piid": 3},
    "CLEANING_MODE": {"siid": 2, "piid": 4},
    "TASK_STATUS": {"siid": 2, "piid": 5},
    "CLEANED_AREA": {"siid": 2, "piid": 6},
    "CLEANING_TIME": {"siid": 2, "piid": 7},
    "SUCTION_LEVEL": {"siid": 2, "piid": 9},
    "WATER_VOLUME": {"siid": 2, "piid": 10},
    "WATER_TANK": {"siid": 2, "piid": 11},
    "SCHEDULE": {"siid": 2, "piid": 19},
    "CARPET_BOOST": {"siid": 2, "piid": 20},
    "RESUME_CLEANING": {"siid": 2, "piid": 23},
    "RELOCATION_STATUS": {"siid": 2, "piid": 26},
    "AUTO_DUST_COLLECTING": {"siid": 2, "piid": 32},
    "AUTO_EMPTY_FREQUENCY": {"siid": 2, "piid": 33},
    "CLEANING_PROPERTIES": {"siid": 2, "piid": 40},
    "FAULTS": {"siid": 2, "piid": 66},
    "CARPET_CLEANING": {"siid": 2, "piid": 73},
    "BATTERY_LEVEL": {"siid": 3, "piid": 1},
    "CHARGING_STATUS": {"siid": 3, "piid": 2},
    "VOLUME": {"siid": 4, "piid": 2},
    "CHILD_LOCK": {"siid": 5, "piid": 1},
    "MOP_PAD_LEFT": {"siid": 9, "piid": 1},
    "MOP_PAD_TIME_LEFT": {"siid": 9, "piid": 2},
    "DND": {"siid": 11, "piid": 1},
    "MAIN_BRUSH_LEFT": {"siid": 12, "piid": 1},
    "MAIN_BRUSH_TIME_LEFT": {"siid": 12, "piid": 2},
    "SIDE_BRUSH_LEFT": {"siid": 13, "piid": 1},
    "SIDE_BRUSH_TIME_LEFT": {"siid": 13, "piid": 2},
    "FILTER_LEFT": {"siid": 14, "piid": 1},
    "FILTER_TIME_LEFT": {"siid": 14, "piid": 2},
    "DETERGENT_LEFT": {"siid": 18, "piid": 1},
}

STATION_ACTIONS: Final[dict[str, dict[str, int]]] = {
    "START": {"siid": 2, "aiid": 1},
    "STOP": {"siid": 2, "aiid": 2},
    "PAUSE": {"siid": 2, "aiid": 7},
    "RESUME": {"siid": 2, "aiid": 8},
    "START_AUTO_EMPTY": {"siid": 2, "aiid": 18},
    "CHARGE": {"siid": 3, "aiid": 1},
    "LOCATE": {"siid": 6, "aiid": 1},
    "RESET_MOP_PAD": {"siid": 9, "aiid": 1},
    "RESET_MAIN_BRUSH": {"siid": 12, "aiid": 1},
    "RESET_SIDE_BRUSH": {"siid": 13, "aiid": 1},
    "RESET_FILTER": {"siid": 14, "aiid": 1},
    "RESET_DETERGENT": {"siid": 18, "aiid": 1},
}

STATION_STATES: Final[dict[int, int]] = wire_map(
    (
        (StationWireState.IDLE, StoredState.IDLE),
        (StationWireState.CHARGING, StoredState.CHARGING),
        (StationWireState.BREAK_CHARGING, StoredState.CHARGING),
        (StationWireState.SWEEPING, StoredState.SWEEPING),
        (StationWireState.PAUSED, StoredState.PAUSED),
        (StationWireState.RETURNING, StoredState.RETURNING),
        (StationWireState.GO_WASH, StoredState.RETURNING_TO_WASH),
        (StationWireState.REMOTE, StoredState.REMOTE_CONTROL),
        (StationWireState.CHARGED, StoredState.CHARGING_COMPLETED),
        (StationWireState.BUILDING, StoredState.BUILDING),
        (StationWireState.UPDATING, StoredState.UPGRADING),
        (StationWireState.MULTI_TASK_STATION, StoredState.STATION_CLEANING),
        (StationWireState.MULTI_TASK_RECHARGE, StoredState.CHARGING),
        (StationWireState.STATION_WORKING, StoredState.STATION_CLEANING),
        (StationWireState.ERROR, StoredState.ERROR),
        (StationWireState.SWEEPING_AND_MOPPING, StoredState.SWEEPING_AND_MOPPING),
        (StationWireState.MOPPING, StoredState.MOPPING),
        (StationWireState.MAPPING_PAUSE, StoredState.PAUSED),
        (StationWireState.GO_CHARGE_BREAK, StoredState.RETURNING),
        (StationWireState.WASH_BREAK, StoredState.RETURNING_TO_WASH),
        (StationWireState.GO_CHARGE_BUILDING, StoredState.BUILDING),
    )
)

STATION_TASKS: Final[dict[int, int]] = wire_map(
    (
        (StationWireTask.GLOBAL, StoredTask.AUTO_CLEANING),
        (StationWireTask.ZONE, StoredTask.ZONE_CLEANING),
        (StationWireTask.AREA, StoredTask.SPOT_CLEANING),
        (StationWireTask.EDGE, StoredTask.ZONE_CLEANING),
        (StationWireTask.CUSTOM, StoredTask.SEGMENT_CLEANING),
        (StationWireTask.POINT, StoredTask.SPOT_CLEANING),
        (StationWireTask.CUSTOM_AREA, StoredTask.ZONE_CLEANING),
    )
)

# The shell maps codes above 18 through the old state enum when new_state is off.
# 23 is washing-paused there, so remote stays on the old remote code 19.
_LEGACY_REMOTE_CONTROL: Final = 19
_OUTSWING_FREQUENCY_OPTIONS: Final[tuple[tuple[int, str], ...]] = (
    (1, "seven_sweeps"),
    (2, "every_time"),
)

STATION_STATISTICS_PROPERTIES: Final[dict[str, dict[str, int]]] = {
    "TOTAL_CLEANED_AREA": {"siid": 2, "piid": 85},
    "CLEANING_COUNT": {"siid": 2, "piid": 86},
    "TOTAL_CLEANING_TIME": {"siid": 2, "piid": 87},
}

DETERGENT_TIME_PROPERTIES: Final[dict[str, dict[str, int]]] = {
    "DETERGENT_TIME_LEFT": {"siid": 18, "piid": 4},
}

# Detergent service 18 is empty on the S60-class spec.
_S60_CLASS_OMITTED_PROPERTIES: Final[frozenset[str]] = frozenset({"DETERGENT_LEFT"})
_S60_CLASS_OMITTED_ACTIONS: Final[frozenset[str]] = frozenset({"RESET_DETERGENT"})
S60_CLASS_PROPERTIES: Final[dict[str, dict[str, int]]] = compose_addresses(
    STATION_PROPERTIES,
    STATION_STATISTICS_PROPERTIES,
    omitted=_S60_CLASS_OMITTED_PROPERTIES,
)
S60_CLASS_ACTIONS: Final[dict[str, dict[str, int]]] = compose_addresses(
    STATION_ACTIONS,
    omitted=_S60_CLASS_OMITTED_ACTIONS,
)

EXTENDED_STATION_STATES: Final[dict[int, int]] = compose_codes(
    STATION_STATES,
    {
        int(StationWireState.REMOTE): _LEGACY_REMOTE_CONTROL,
        int(ExtendedStationWireState.STATION_ASSISTING): int(StoredState.WASHING),
        int(ExtendedStationWireState.STATION_ASSISTED): int(
            StoredState.CHARGING_COMPLETED
        ),
        int(ExtendedStationWireState.RETURNING_DURING_ASSIST): int(
            StoredState.RETURNING
        ),
    },
)

# Old code 25 is water check. Self-check has no shell state of its own.
_UNKNOWN_SHELL_STATE: Final = -1

SUMMON_STATES: Final[dict[int, int]] = {
    int(SummonWireState.SELF_CHECK): _UNKNOWN_SHELL_STATE,
    int(SummonWireState.SUMMONING): int(StoredState.CLEAN_SUMMON),
}

# Sweep-summon has no shell state of its own, so it stays sweeping.
SWEEP_SUMMON_STATES: Final[dict[int, int]] = {
    int(SummonWireState.SWEEP_SUMMONING): int(StoredState.SWEEPING),
}

# Status runs through sweep-summon 27 and keeps station assist 22 and 23.
S60_CLASS_STATES: Final[dict[int, int]] = compose_codes(
    EXTENDED_STATION_STATES,
    {**SUMMON_STATES, **SWEEP_SUMMON_STATES},
)

EXTENDED_STATION_TASKS: Final[dict[int, int]] = compose_codes(
    STATION_TASKS,
    {
        int(ExtendedStationWireTask.APPOINTMENT): int(StoredTask.AUTO_CLEANING),
        int(ExtendedStationWireTask.LINKAGE): int(StoredTask.AUTO_CLEANING),
        int(ExtendedStationWireTask.FAST_MAPPING): int(StoredTask.FAST_MAPPING),
        int(ExtendedStationWireTask.AI_HOSTING): int(StoredTask.AUTO_CLEANING),
    },
)

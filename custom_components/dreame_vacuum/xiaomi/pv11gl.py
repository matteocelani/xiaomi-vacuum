"""Xiaomi Robot Vacuum 6 Max record composed from the camera roller profile."""

from __future__ import annotations

from typing import Final

from .model import MODEL_ROBOT_VACUUM_6_MAX, XiaomiModel
from .profile import (
    CAMERA_ROLLER_CONTROLS,
    CAMERA_ROLLER_OMITTED_CONTROLS,
    DETERGENT_TIME_PROPERTIES,
    EXTENDED_STATION_CONTROLS,
    EXTENDED_STATION_STATES,
    EXTENDED_STATION_TASKS,
    HOST_TANK_WITH_NOT_INSTALLED,
    PRECISE_DIAGNOSIS,
    STATION_ACTIONS,
    STATION_PROPERTIES,
    STATION_STATISTICS_PROPERTIES,
    SUMMON_STATES,
    SWEEP_SUMMON_STATES,
    WATER_LEVEL_REMIND,
    WORRY_FREE_THROUGH_BUTLER,
    ExtendedStationWireState,
    compose_addresses,
    compose_codes,
    compose_controls,
)

# The Dreame cleaning-mode select would write mop-only, which this spec omits.
_OMITTED_PROPERTIES: Final = frozenset({"CLEANING_MODE"})

ROBOT_VACUUM_6_MAX: Final = XiaomiModel(
    model=MODEL_ROBOT_VACUUM_6_MAX,
    property_overrides=compose_addresses(
        STATION_PROPERTIES,
        compose_addresses(STATION_STATISTICS_PROPERTIES, DETERGENT_TIME_PROPERTIES),
        omitted=_OMITTED_PROPERTIES,
    ),
    action_overrides=compose_addresses(STATION_ACTIONS),
    state_by_wire=compose_codes(
        EXTENDED_STATION_STATES,
        {**SUMMON_STATES, **SWEEP_SUMMON_STATES},
        omitted=(
            int(ExtendedStationWireState.STATION_ASSISTING),
            int(ExtendedStationWireState.STATION_ASSISTED),
        ),
    ),
    task_by_wire=compose_codes(EXTENDED_STATION_TASKS),
    controls=compose_controls(
        EXTENDED_STATION_CONTROLS,
        (*CAMERA_ROLLER_CONTROLS, PRECISE_DIAGNOSIS, WATER_LEVEL_REMIND),
        omitted=CAMERA_ROLLER_OMITTED_CONTROLS,
        replaced={
            "xiaomi_host_tank": HOST_TANK_WITH_NOT_INSTALLED,
            "xiaomi_worry_free_mode": WORRY_FREE_THROUGH_BUTLER,
        },
    ),
)

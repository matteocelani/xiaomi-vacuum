"""Xiaomi Robot Vacuum 6 Pro record composed from the camera roller profile."""

from __future__ import annotations

from typing import Final

from .model import MODEL_ROBOT_VACUUM_6_PRO, XiaomiModel
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
    WATER_LEVEL_REMIND,
    compose_addresses,
    compose_codes,
    compose_controls,
)

# Service 9 is empty, and the Dreame cleaning-mode select would write mop-only.
_OMITTED_PROPERTIES: Final = frozenset(
    {
        "CLEANING_MODE",
        "MOP_PAD_LEFT",
        "MOP_PAD_TIME_LEFT",
    }
)
_OMITTED_ACTIONS: Final = frozenset({"RESET_MOP_PAD"})

ROBOT_VACUUM_6_PRO: Final = XiaomiModel(
    model=MODEL_ROBOT_VACUUM_6_PRO,
    property_overrides=compose_addresses(
        STATION_PROPERTIES,
        compose_addresses(STATION_STATISTICS_PROPERTIES, DETERGENT_TIME_PROPERTIES),
        omitted=_OMITTED_PROPERTIES,
    ),
    action_overrides=compose_addresses(STATION_ACTIONS, omitted=_OMITTED_ACTIONS),
    # Sweep-summon 27 is not published. Station assist 22 and 23 stay.
    state_by_wire=compose_codes(EXTENDED_STATION_STATES, SUMMON_STATES),
    task_by_wire=compose_codes(EXTENDED_STATION_TASKS),
    controls=compose_controls(
        EXTENDED_STATION_CONTROLS,
        (*CAMERA_ROLLER_CONTROLS, PRECISE_DIAGNOSIS, WATER_LEVEL_REMIND),
        omitted=CAMERA_ROLLER_OMITTED_CONTROLS,
        # Worry-free keeps the shared list, which publishes pet.
        replaced={"xiaomi_host_tank": HOST_TANK_WITH_NOT_INSTALLED},
    ),
)

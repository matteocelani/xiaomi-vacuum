"""Xiaomi Robot Vacuum 5 Pro record composed from the extended station profile."""

from __future__ import annotations

from typing import Final

from .model import MODEL_ROBOT_VACUUM_5_PRO, XiaomiModel
from .profile import (
    DETERGENT_TIME_PROPERTIES,
    EXTENDED_STATION_CONTROLS,
    EXTENDED_STATION_STATES,
    EXTENDED_STATION_TASKS,
    S40_CLASS_CONTROLS,
    SOLID_DIRT_DETECTION,
    STATION_ACTIONS,
    STATION_PROPERTIES,
    STATION_STATISTICS_PROPERTIES,
    STREAM_CONTROLS,
    compose_addresses,
    compose_codes,
    compose_controls,
    control_with_options,
)

# This spec names value 0 Silent and value 2 Standard. The shared list does not.
_WORRY_FREE_MODE: Final = control_with_options(
    EXTENDED_STATION_CONTROLS,
    "xiaomi_worry_free_mode",
    (
        (0, "silent"),
        (1, "deep_clean"),
        (2, "standard"),
        (3, "butler"),
        (4, "pet"),
    ),
)

_ADDED_CONTROLS: Final = (SOLID_DIRT_DETECTION, *STREAM_CONTROLS)

ROBOT_VACUUM_5_PRO: Final = XiaomiModel(
    model=MODEL_ROBOT_VACUUM_5_PRO,
    property_overrides=compose_addresses(
        STATION_PROPERTIES,
        compose_addresses(STATION_STATISTICS_PROPERTIES, DETERGENT_TIME_PROPERTIES),
    ),
    action_overrides=compose_addresses(STATION_ACTIONS),
    state_by_wire=compose_codes(EXTENDED_STATION_STATES),
    task_by_wire=compose_codes(EXTENDED_STATION_TASKS),
    controls=compose_controls(
        EXTENDED_STATION_CONTROLS,
        S40_CLASS_CONTROLS + _ADDED_CONTROLS,
        replaced={"xiaomi_worry_free_mode": _WORRY_FREE_MODE},
    ),
)

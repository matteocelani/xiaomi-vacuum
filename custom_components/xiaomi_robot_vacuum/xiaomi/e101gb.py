"""Xiaomi Robot Vacuum S40C record composed from the S40-class station profile."""

from __future__ import annotations

from typing import Final

from .model import MODEL_S40C, XiaomiModel
from .profile import (
    DETERGENT_TIME_PROPERTIES,
    EXTENDED_STATION_CONTROLS,
    EXTENDED_STATION_STATES,
    EXTENDED_STATION_TASKS,
    S40_CLASS_CONTROLS,
    S40_CLASS_OMITTED_CONTROLS,
    STATION_ACTIONS,
    STATION_PROPERTIES,
    STATION_STATISTICS_PROPERTIES,
    compose_addresses,
    compose_codes,
    compose_controls,
    control_with_options,
)

# The spec drops mop-wash enable, stop-dry, and both cut-hair actions.
_OMITTED_CONTROLS: Final = S40_CLASS_OMITTED_CONTROLS | frozenset(
    {
        "xiaomi_enable_mop_wash",
        "xiaomi_start_cut_hair",
        "xiaomi_stop_cut_hair",
        "xiaomi_stop_dry",
    }
)
# Values 0 and 1 are both Deep Clean. Distinct slugs keep each wire value writable.
_WORRY_FREE_MODE: Final = control_with_options(
    EXTENDED_STATION_CONTROLS,
    "xiaomi_worry_free_mode",
    (
        (0, "deep_clean"),
        (1, "deep_clean_2"),
        (2, "general"),
        (3, "butler"),
        (4, "pet"),
    ),
)

S40C: Final = XiaomiModel(
    model=MODEL_S40C,
    property_overrides=compose_addresses(
        STATION_PROPERTIES,
        compose_addresses(STATION_STATISTICS_PROPERTIES, DETERGENT_TIME_PROPERTIES),
    ),
    action_overrides=compose_addresses(STATION_ACTIONS),
    state_by_wire=compose_codes(EXTENDED_STATION_STATES),
    task_by_wire=compose_codes(EXTENDED_STATION_TASKS),
    controls=compose_controls(
        EXTENDED_STATION_CONTROLS,
        S40_CLASS_CONTROLS,
        omitted=_OMITTED_CONTROLS,
        replaced={"xiaomi_worry_free_mode": _WORRY_FREE_MODE},
    ),
)

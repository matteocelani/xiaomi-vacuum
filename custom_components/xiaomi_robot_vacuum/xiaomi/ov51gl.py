"""Xiaomi Robot Vacuum H40 record composed from the S40-class station profile."""

from __future__ import annotations

from typing import Final

from .model import MODEL_H40, XiaomiModel
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
)

# Version 1 publishes dust-arrest-complete 2.3 and omits detergent reminder 2.71.
_OMITTED_CONTROLS: Final = S40_CLASS_OMITTED_CONTROLS | frozenset(
    {"xiaomi_detergent_reminder"}
)

H40: Final = XiaomiModel(
    model=MODEL_H40,
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
    ),
)

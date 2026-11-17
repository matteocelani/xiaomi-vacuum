"""Xiaomi Robot Vacuum S40 record composed from the S40-class station profile."""

from __future__ import annotations

from typing import Final

from .model import MODEL_S40, XiaomiModel
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

S40: Final = XiaomiModel(
    model=MODEL_S40,
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
        omitted=S40_CLASS_OMITTED_CONTROLS,
    ),
)

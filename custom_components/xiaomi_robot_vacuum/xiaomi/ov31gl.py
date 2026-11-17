"""Xiaomi Robot Vacuum 5 record composed from the station profile."""

from __future__ import annotations

from typing import Final

from .model import MODEL_ROBOT_VACUUM_5, XiaomiModel
from .profile import (
    DETERGENT_TIME_PROPERTIES,
    EXTENDED_STATION_CONTROLS,
    EXTENDED_STATION_STATES,
    EXTENDED_STATION_TASKS,
    PRECISE_DIAGNOSIS,
    STATION_ACTIONS,
    STATION_PROPERTIES,
    STATION_STATISTICS_PROPERTIES,
    compose_addresses,
    compose_codes,
    compose_controls,
)

_PROPERTIES: Final[dict[str, dict[str, int]]] = compose_addresses(
    STATION_STATISTICS_PROPERTIES,
    DETERGENT_TIME_PROPERTIES,
)

ROBOT_VACUUM_5: Final = XiaomiModel(
    model=MODEL_ROBOT_VACUUM_5,
    property_overrides=compose_addresses(STATION_PROPERTIES, _PROPERTIES),
    action_overrides=compose_addresses(STATION_ACTIONS),
    state_by_wire=compose_codes(EXTENDED_STATION_STATES),
    task_by_wire=compose_codes(EXTENDED_STATION_TASKS),
    controls=compose_controls(EXTENDED_STATION_CONTROLS, (PRECISE_DIAGNOSIS,)),
)

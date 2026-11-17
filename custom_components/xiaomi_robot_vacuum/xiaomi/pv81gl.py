"""Xiaomi Robot Vacuum S60 record composed from the S60-class profile."""

from __future__ import annotations

from typing import Final

from .model import MODEL_S60, XiaomiModel
from .profile import (
    EXTENDED_STATION_CONTROLS,
    EXTENDED_STATION_TASKS,
    S60_CLASS_ACTIONS,
    S60_CLASS_CONTROLS,
    S60_CLASS_PROPERTIES,
    S60_CLASS_STATES,
    compose_addresses,
    compose_codes,
    compose_controls,
    select_controls,
)

# The charging dock publishes no auto-empty station.
_OMITTED_PROPERTIES: Final = frozenset(
    {
        "AUTO_DUST_COLLECTING",
        "AUTO_EMPTY_FREQUENCY",
    }
)
_OMITTED_ACTIONS: Final = frozenset({"START_AUTO_EMPTY"})

S60: Final = XiaomiModel(
    model=MODEL_S60,
    property_overrides=compose_addresses(
        S60_CLASS_PROPERTIES,
        omitted=_OMITTED_PROPERTIES,
    ),
    action_overrides=compose_addresses(S60_CLASS_ACTIONS, omitted=_OMITTED_ACTIONS),
    state_by_wire=compose_codes(S60_CLASS_STATES),
    task_by_wire=compose_codes(EXTENDED_STATION_TASKS),
    controls=compose_controls(
        S60_CLASS_CONTROLS,
        select_controls(EXTENDED_STATION_CONTROLS, ("xiaomi_stop_cut_hair",)),
    ),
)

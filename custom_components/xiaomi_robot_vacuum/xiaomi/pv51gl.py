"""Xiaomi Robot Vacuum S60+ record composed from the S60-class profile."""

from __future__ import annotations

from typing import Final

from .model import MODEL_S60_PLUS, XiaomiModel
from .profile import (
    EXTENDED_STATION_CONTROLS,
    EXTENDED_STATION_TASKS,
    S60_CLASS_ACTIONS,
    S60_CLASS_CONTROLS,
    S60_CLASS_PROPERTIES,
    S60_CLASS_STATES,
    SWEEP_DUST_ARREST,
    compose_addresses,
    compose_codes,
    compose_controls,
    select_controls,
)

# The auto-empty dock publishes these. S60 leaves the same addresses out.
_DUST_STATION_CONTROLS: Final = (
    *select_controls(
        EXTENDED_STATION_CONTROLS,
        (
            "xiaomi_dust_arrest_power",
            "xiaomi_dust_bag_life",
            "xiaomi_dust_bag_time_left",
            "xiaomi_reset_dust_bag",
        ),
    ),
    SWEEP_DUST_ARREST,
)

S60_PLUS: Final = XiaomiModel(
    model=MODEL_S60_PLUS,
    property_overrides=compose_addresses(S60_CLASS_PROPERTIES),
    action_overrides=compose_addresses(S60_CLASS_ACTIONS),
    state_by_wire=compose_codes(S60_CLASS_STATES),
    task_by_wire=compose_codes(EXTENDED_STATION_TASKS),
    controls=compose_controls(S60_CLASS_CONTROLS, _DUST_STATION_CONTROLS),
)

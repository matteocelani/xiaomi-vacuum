"""Xiaomi Robot Vacuum H50 Pro Roller record composed from the H50 roller profile."""

from __future__ import annotations

from typing import Final

from .model import MODEL_H50_PRO_ROLLER, XiaomiModel
from .profile import (
    AI_CAMERA_CONTROLS,
    EXTENDED_STATION_CONTROLS,
    EXTENDED_STATION_TASKS,
    H50_ROLLER_ACTIONS,
    H50_ROLLER_CONTROLS,
    H50_ROLLER_PROPERTIES,
    H50_ROLLER_STATES,
    compose_addresses,
    compose_codes,
    compose_controls,
    select_controls,
)

# Mop-only is not published, so the Dreame cleaning-mode select must stay off.
_OMITTED_PROPERTIES: Final = frozenset({"CLEANING_MODE"})
# Start eject and sweep AI detection are published only on this spec.
_ADDED_CONTROLS: Final = (
    *select_controls(EXTENDED_STATION_CONTROLS, ("xiaomi_start_eject",)),
    *select_controls(AI_CAMERA_CONTROLS, ("xiaomi_sweep_ai_detection",)),
)

H50_PRO_ROLLER: Final = XiaomiModel(
    model=MODEL_H50_PRO_ROLLER,
    property_overrides=compose_addresses(
        H50_ROLLER_PROPERTIES,
        omitted=_OMITTED_PROPERTIES,
    ),
    action_overrides=compose_addresses(H50_ROLLER_ACTIONS),
    state_by_wire=compose_codes(H50_ROLLER_STATES),
    task_by_wire=compose_codes(EXTENDED_STATION_TASKS),
    controls=compose_controls(H50_ROLLER_CONTROLS, _ADDED_CONTROLS),
)

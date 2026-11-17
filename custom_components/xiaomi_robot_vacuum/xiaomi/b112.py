"""Xiaomi Robot Vacuum E10 record on the sweep spec family."""

from __future__ import annotations

from typing import Final

from .model import (
    MODEL_E10,
    XiaomiModel,
    compose_addresses,
    compose_codes,
    compose_controls,
)
from .sweep import (
    SWEEP_ACTIONS,
    SWEEP_CONTROLS,
    SWEEP_PROPERTIES,
    SWEEP_STATES,
)

E10: Final = XiaomiModel(
    model=MODEL_E10,
    property_overrides=compose_addresses(SWEEP_PROPERTIES),
    action_overrides=compose_addresses(SWEEP_ACTIONS),
    state_by_wire=compose_codes(SWEEP_STATES),
    task_by_wire={},
    controls=compose_controls(SWEEP_CONTROLS),
)

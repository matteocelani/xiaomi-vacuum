"""Mijia G1 record on the Essential spec family."""

from __future__ import annotations

from typing import Final

from .essential import (
    ESSENTIAL_ACTIONS,
    ESSENTIAL_CONTROLS,
    ESSENTIAL_PROPERTIES,
    ESSENTIAL_STATES,
)
from .model import (
    MODEL_MIJIA_G1,
    XiaomiModel,
    compose_addresses,
    compose_codes,
    compose_controls,
)

G1: Final[XiaomiModel] = XiaomiModel(
    model=MODEL_MIJIA_G1,
    property_overrides=compose_addresses(ESSENTIAL_PROPERTIES),
    action_overrides=compose_addresses(ESSENTIAL_ACTIONS),
    state_by_wire=compose_codes(ESSENTIAL_STATES),
    task_by_wire={},
    controls=compose_controls(ESSENTIAL_CONTROLS),
)

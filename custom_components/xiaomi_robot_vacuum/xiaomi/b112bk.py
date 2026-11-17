"""Xiaomi Robot Vacuum E10C record on the sweep spec family."""

from __future__ import annotations

from typing import Final

from .model import (
    MODEL_E10C,
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

# Released v1 matches E10. Debug v2 is not used. Timezone range differs and stays omitted.
E10C: Final = XiaomiModel(
    model=MODEL_E10C,
    property_overrides=compose_addresses(SWEEP_PROPERTIES),
    action_overrides=compose_addresses(SWEEP_ACTIONS),
    state_by_wire=compose_codes(SWEEP_STATES),
    task_by_wire={},
    controls=compose_controls(SWEEP_CONTROLS),
)

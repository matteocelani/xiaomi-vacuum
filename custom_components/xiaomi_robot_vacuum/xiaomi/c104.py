"""Mijia Sweep Mop 3 record. Status order and the alarm list differ from S12."""

from __future__ import annotations

from enum import IntEnum
from typing import Final

from .b106eu import S12
from .model import (
    MODEL_MIJIA_SWEEP_MOP_3,
    StoredState,
    XiaomiModel,
    regional_variant,
    select_controls,
)
from .sweep import SWEEP_CONTROLS


class _StatusWire(IntEnum):
    """Status wires this spec orders like the shared sweep list, not S12."""

    SWEEPING_AND_MOPPING = 6
    MOPPING = 7


# The released alarm is the shared play list, not S12's boolean.
_SHARED_ALARM: Final = select_controls(SWEEP_CONTROLS, ("xiaomi_alarm",))[0]

MIJIA_SWEEP_MOP_3: Final[XiaomiModel] = regional_variant(
    S12,
    MODEL_MIJIA_SWEEP_MOP_3,
    control_replaced={"xiaomi_alarm": _SHARED_ALARM},
    state_overrides={
        int(_StatusWire.SWEEPING_AND_MOPPING): int(StoredState.SWEEPING_AND_MOPPING),
        int(_StatusWire.MOPPING): int(StoredState.MOPPING),
    },
)

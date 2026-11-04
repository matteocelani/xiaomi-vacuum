"""Mijia Sweep Mop 2S record. Carpet cleaning is absent; sweep-type adds edge and point."""

from __future__ import annotations

from enum import IntEnum
from typing import Final

from .b108gl import S20_PLUS
from .model import (
    MODEL_MIJIA_SWEEP_MOP_2S,
    StoredTask,
    XiaomiModel,
    regional_variant,
)

# The shell relabels codes above 18 through the old state enum while new_state is off.
_LEGACY_REMOTE_CONTROL: Final = 19


class _RemoteStatus(IntEnum):
    """Status wire the released spec calls Remote."""

    REMOTE = 7


class _SweepTypeWire(IntEnum):
    """Sweep-type codes this spec adds beside the S20+ list."""

    EDGE = 2
    POINT = 3


MIJIA_SWEEP_MOP_2S: Final[XiaomiModel] = regional_variant(
    S20_PLUS,
    MODEL_MIJIA_SWEEP_MOP_2S,
    property_omitted=("CARPET_CLEANING",),
    state_overrides={int(_RemoteStatus.REMOTE): _LEGACY_REMOTE_CONTROL},
    task_overrides={
        int(_SweepTypeWire.EDGE): int(StoredTask.ZONE_CLEANING),
        int(_SweepTypeWire.POINT): int(StoredTask.SPOT_CLEANING),
    },
)

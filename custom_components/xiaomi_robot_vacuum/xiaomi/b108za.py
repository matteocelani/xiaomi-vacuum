"""Mijia Sweep Mop 2S record. Carpet cleaning is absent; sweep-type adds edge and point."""

from __future__ import annotations

from enum import IntEnum
from typing import Final

from .b108gl import S20_PLUS
from .controls import boolean_switch
from .model import (
    MODEL_MIJIA_SWEEP_MOP_2S,
    StoredTask,
    XiaomiModel,
    control_with_options,
    regional_variant,
)

# This spec has no wire 3. Full Speed is 4.
_FAN_MODE: Final = control_with_options(
    S20_PLUS.controls,
    "xiaomi_fan_mode",
    ((1, "silent"), (2, "basic"), (4, "full_speed")),
)
# Station carpet avoidance is siid 2 piid 21. This spec uses siid 6 piid 7.
_CARPET_AVOIDANCE: Final = boolean_switch("xiaomi_carpet_avoidance", 6, 7)

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
    control_omitted=(
        "xiaomi_edge_swing_tail_sweep",
        "xiaomi_edge_sweep_frequency",
        "xiaomi_carpet_discriminate",
    ),
    control_replaced={"xiaomi_fan_mode": _FAN_MODE},
    control_additions=(_CARPET_AVOIDANCE,),
    state_overrides={int(_RemoteStatus.REMOTE): _LEGACY_REMOTE_CONTROL},
    task_overrides={
        int(_SweepTypeWire.EDGE): int(StoredTask.ZONE_CLEANING),
        int(_SweepTypeWire.POINT): int(StoredTask.SPOT_CLEANING),
    },
)

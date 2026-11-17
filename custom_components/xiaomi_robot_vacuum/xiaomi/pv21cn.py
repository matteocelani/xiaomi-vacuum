"""Mijia 6 Pro record. Worry-free stops at butler and the swing control is absent."""

from __future__ import annotations

from typing import Final

from .model import MODEL_MIJIA_6_PRO, XiaomiModel, regional_variant
from .profile import WORRY_FREE_THROUGH_BUTLER
from .pv21gl import ROBOT_VACUUM_6_PRO

_OMITTED_CONTROLS: Final = frozenset(
    {
        "xiaomi_call_clean",
        "xiaomi_mop_outer_swing",
    }
)

MIJIA_6_PRO: Final[XiaomiModel] = regional_variant(
    ROBOT_VACUUM_6_PRO,
    MODEL_MIJIA_6_PRO,
    control_omitted=_OMITTED_CONTROLS,
    control_replaced={"xiaomi_worry_free_mode": WORRY_FREE_THROUGH_BUTLER},
)

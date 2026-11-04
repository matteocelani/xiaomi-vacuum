"""Essential v3 record. Start Charge moves to the battery service."""

from __future__ import annotations

from typing import Final

from .model import (
    MODEL_MIJIA_ESSENTIAL_V3,
    XiaomiModel,
    control_with_options,
    regional_variant,
)
from .v1 import G1

_BATTERY_SERVICE: Final = 3
_START_CHARGE_ACTION: Final = 1
_LANGUAGE_OPTIONS: Final[tuple[tuple[int, str], ...]] = (
    (0, "traditional_chinese"),
    (1, "english"),
)

ESSENTIAL_V3: Final[XiaomiModel] = regional_variant(
    G1,
    MODEL_MIJIA_ESSENTIAL_V3,
    action_additions={
        "CHARGE": {"siid": _BATTERY_SERVICE, "aiid": _START_CHARGE_ACTION}
    },
    control_replaced={
        "xiaomi_voice_language": control_with_options(
            G1.controls, "xiaomi_voice_language", _LANGUAGE_OPTIONS
        )
    },
)

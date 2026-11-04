"""Essential v2 record. Released version 1 matches G1 except voice language."""

from __future__ import annotations

from typing import Final

from .essential import ESSENTIAL_CLEAR_CODE, ESSENTIAL_NO_FAULTS
from .model import (
    MODEL_MIJIA_ESSENTIAL,
    XiaomiModel,
    control_with_options,
    regional_variant,
)
from .v1 import G1

_LANGUAGE_OPTIONS: Final[tuple[tuple[int, str], ...]] = (
    (0, "english"),
    (1, "simplified_chinese"),
    (2, "spanish"),
    (3, "russian"),
    (4, "italian"),
    (5, "french"),
    (6, "german"),
    (7, "korean"),
    (8, "polish"),
)

ESSENTIAL: Final[XiaomiModel] = regional_variant(
    G1,
    MODEL_MIJIA_ESSENTIAL,
    control_replaced={
        "xiaomi_voice_language": control_with_options(
            G1.controls, "xiaomi_voice_language", _LANGUAGE_OPTIONS
        )
    },
    fault_overrides={ESSENTIAL_CLEAR_CODE: ESSENTIAL_NO_FAULTS},
)

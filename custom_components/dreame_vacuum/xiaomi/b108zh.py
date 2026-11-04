"""Mijia Sweep Mop 3S domestic record. The released value set matches the 2S spec."""

from __future__ import annotations

from typing import Final

from .b108za import MIJIA_SWEEP_MOP_2S
from .model import MODEL_MIJIA_SWEEP_MOP_3S_ZH, XiaomiModel, alias_model

MIJIA_SWEEP_MOP_3S_ZH: Final[XiaomiModel] = alias_model(
    MIJIA_SWEEP_MOP_2S, MODEL_MIJIA_SWEEP_MOP_3S_ZH
)

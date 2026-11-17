"""Mijia sweep-mop 2 record. Unmapped voice and map gaps make this an X20 alias."""

from __future__ import annotations

from typing import Final

from .c101eu import X20
from .model import MODEL_MIJIA_SWEEP_MOP_2, XiaomiModel, alias_model

MIJIA_SWEEP_MOP_2: Final[XiaomiModel] = alias_model(X20, MODEL_MIJIA_SWEEP_MOP_2)

"""Mijia 5C record. The released spec matches H50 Pro, so this is an alias."""

from __future__ import annotations

from typing import Final

from .model import MODEL_MIJIA_5C, XiaomiModel, alias_model
from .ov42gl import H50_PRO

MIJIA_5C: Final[XiaomiModel] = alias_model(H50_PRO, MODEL_MIJIA_5C)

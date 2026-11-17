"""Mijia 3C record. Wire 10 is Charged, unlike the S20 Charging label."""

from __future__ import annotations

from enum import IntEnum
from typing import Final

from .d106gl import S20
from .model import MODEL_MIJIA_3C, StoredState, XiaomiModel, regional_variant


class _ChargedStatus(IntEnum):
    """Status code the Chinese spec labels Charged."""

    CHARGED = 10


MIJIA_3C: Final[XiaomiModel] = regional_variant(
    S20,
    MODEL_MIJIA_3C,
    state_overrides={int(_ChargedStatus.CHARGED): int(StoredState.CHARGING_COMPLETED)},
)

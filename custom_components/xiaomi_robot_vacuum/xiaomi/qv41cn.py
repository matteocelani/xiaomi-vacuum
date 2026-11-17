"""Mijia 7C record, the Chinese qv41cn variant of the H50 Pro Roller."""

from __future__ import annotations

from typing import Final

from .model import MODEL_MIJIA_7C, XiaomiModel, regional_variant
from .qv41gl import H50_PRO_ROLLER

# The Chinese spec does not publish wash-mop water temperature.
_OMITTED_CONTROLS: Final = frozenset({"xiaomi_wash_water_temperature"})

MIJIA_7C: Final[XiaomiModel] = regional_variant(
    H50_PRO_ROLLER,
    MODEL_MIJIA_7C,
    control_omitted=_OMITTED_CONTROLS,
)

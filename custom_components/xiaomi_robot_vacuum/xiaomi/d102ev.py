"""Mijia M30 record, the EV variant of X20 Pro with a shorter value list."""

from __future__ import annotations

from typing import Final

from .d102gl import X20_PRO
from .model import (
    MODEL_MIJIA_M30,
    XiaomiModel,
    control_with_options,
    regional_variant,
    select_controls,
)
from .profile import EXTENDED_STATION_CONTROLS

# The Chinese spec stops before By Time and before Span.
_MOP_WASH_FREQUENCY: Final = control_with_options(
    EXTENDED_STATION_CONTROLS,
    "xiaomi_mop_wash_frequency",
    (
        (0, "by_room"),
        (1, "by_area"),
    ),
)
_CARPET_CLEANING: Final = control_with_options(
    EXTENDED_STATION_CONTROLS,
    "xiaomi_carpet_cleaning_method",
    (
        (0, "self_adaption"),
        (1, "avoid"),
        (2, "ignore"),
    ),
)
_OMITTED_CONTROLS: Final = frozenset(
    {
        "xiaomi_carpet_deep_cleaning",
        "xiaomi_carpet_discriminate",
        "xiaomi_sweep_carpet_first",
    }
)
_HOT_WATER_WASH: Final = select_controls(
    EXTENDED_STATION_CONTROLS, ("xiaomi_hot_water_wash",)
)

MIJIA_M30: Final[XiaomiModel] = regional_variant(
    X20_PRO,
    MODEL_MIJIA_M30,
    control_additions=_HOT_WATER_WASH,
    control_omitted=_OMITTED_CONTROLS,
    control_replaced={
        "xiaomi_carpet_cleaning_method": _CARPET_CLEANING,
        "xiaomi_mop_wash_frequency": _MOP_WASH_FREQUENCY,
    },
)

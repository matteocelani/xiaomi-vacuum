"""Mijia M30 Pro record. Camera and hair-cutting switches are the diff from Mijia M30."""

from __future__ import annotations

from typing import Final

from .d102ev import MIJIA_M30
from .model import (
    MODEL_MIJIA_M30_PRO,
    XiaomiModel,
    regional_variant,
    select_controls,
)
from .profile import (
    DETERGENT_TIME_PROPERTIES,
    EXTENDED_STATION_CONTROLS,
    S40_CLASS_CONTROLS,
    SOLID_DIRT_DETECTION,
)

# M30 publishes wire 1 as every time. This spec uses the S40 order.
_STANDARD_EDGE_SWEEP: Final = select_controls(
    S40_CLASS_CONTROLS, ("xiaomi_edge_sweep_frequency",)
)[0]
_ADDED_CONTROLS: Final = (
    *select_controls(
        EXTENDED_STATION_CONTROLS,
        (
            "xiaomi_calibrate_imu",
            "xiaomi_call_clean",
            "xiaomi_carpet_deep_cleaning",
            "xiaomi_carpet_discriminate",
            "xiaomi_start_cut_hair",
            "xiaomi_stop_cut_hair",
        ),
    ),
    *select_controls(
        S40_CLASS_CONTROLS,
        (
            "xiaomi_ai_cleaning",
            "xiaomi_ai_managed_cleaning",
            "xiaomi_cut_hair",
            "xiaomi_cut_hair_frequency",
            "xiaomi_defecation_detection",
            "xiaomi_dirt_detection",
            "xiaomi_floor_material_detection",
            "xiaomi_liquid_dirt_detection",
            "xiaomi_mop_auto_lift",
            "xiaomi_object_detection",
            "xiaomi_room_detection",
            "xiaomi_sweep_ai_detection",
        ),
    ),
    SOLID_DIRT_DETECTION,
)

MIJIA_M30_PRO: Final[XiaomiModel] = regional_variant(
    MIJIA_M30,
    MODEL_MIJIA_M30_PRO,
    property_additions=DETERGENT_TIME_PROPERTIES,
    control_additions=_ADDED_CONTROLS,
    control_replaced={"xiaomi_edge_sweep_frequency": _STANDARD_EDGE_SWEEP},
)

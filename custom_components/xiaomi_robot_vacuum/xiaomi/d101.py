"""Mijia H40 record. The spec follows X20 Pro without dust collection, voice, or detergent."""

from __future__ import annotations

from typing import Final

from .d102gl import X20_PRO
from .model import (
    MODEL_MIJIA_H40,
    StoredState,
    XiaomiModel,
    control_with_options,
    regional_variant,
    select_controls,
)
from .profile import (
    DRYING_TIME_THROUGH_TWELVE_HOURS,
    EXTENDED_STATION_CONTROLS,
    ExtendedStationWireState,
)

_BY_ROOM: Final = 0
_BY_AREA: Final = 1
_MOP_WASH_FREQUENCY: Final = control_with_options(
    EXTENDED_STATION_CONTROLS,
    "xiaomi_mop_wash_frequency",
    (
        (_BY_ROOM, "by_room"),
        (_BY_AREA, "by_area"),
    ),
)
_OMITTED_PROPERTIES: Final = frozenset(
    {
        "AUTO_DUST_COLLECTING",
        "AUTO_EMPTY_FREQUENCY",
        "DETERGENT_LEFT",
    }
)
_OMITTED_ACTIONS: Final = frozenset({"RESET_DETERGENT", "START_AUTO_EMPTY"})
_OMITTED_CONTROLS: Final = frozenset(
    {
        "xiaomi_auto_water_change",
        "xiaomi_auto_water_change_installed",
        "xiaomi_cancel_water_check",
        "xiaomi_carpet_discriminate",
        "xiaomi_current_voice",
        "xiaomi_detergent_delivery",
        "xiaomi_detergent_level",
        "xiaomi_detergent_reminder",
        "xiaomi_detergent_self_delivery",
        "xiaomi_download_progress",
        "xiaomi_download_status",
        "xiaomi_dust_bag_life",
        "xiaomi_dust_bag_time_left",
        "xiaomi_reset_dust_bag",
        "xiaomi_start_water_check",
        "xiaomi_use_detergent",
        "xiaomi_voltage",
        "xiaomi_water_check_status",
    }
)
_ADDED_CONTROLS: Final = select_controls(
    EXTENDED_STATION_CONTROLS,
    (
        "xiaomi_start_station_cleaning",
        "xiaomi_stop_working",
        "xiaomi_sweep_before_mop",
        "xiaomi_sweep_mop_status",
    ),
)
_ASSIST_STATES: Final = {
    int(ExtendedStationWireState.STATION_ASSISTING): int(StoredState.WASHING),
    int(ExtendedStationWireState.STATION_ASSISTED): int(StoredState.CHARGING_COMPLETED),
    int(ExtendedStationWireState.RETURNING_DURING_ASSIST): int(StoredState.RETURNING),
}

MIJIA_H40: Final[XiaomiModel] = regional_variant(
    X20_PRO,
    MODEL_MIJIA_H40,
    property_omitted=_OMITTED_PROPERTIES,
    action_omitted=_OMITTED_ACTIONS,
    control_additions=_ADDED_CONTROLS,
    control_omitted=_OMITTED_CONTROLS,
    control_replaced={
        "xiaomi_drying_time": DRYING_TIME_THROUGH_TWELVE_HOURS,
        "xiaomi_mop_wash_frequency": _MOP_WASH_FREQUENCY,
    },
    state_overrides=_ASSIST_STATES,
)

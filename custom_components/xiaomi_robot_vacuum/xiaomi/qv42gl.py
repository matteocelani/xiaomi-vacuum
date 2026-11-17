"""Xiaomi Robot Vacuum H50 Roller record composed from the H50 roller profile."""

from __future__ import annotations

from typing import Final

from .model import MODEL_H50_ROLLER, XiaomiModel
from .profile import (
    EXTENDED_STATION_CONTROLS,
    EXTENDED_STATION_TASKS,
    H50_ROLLER_ACTIONS,
    H50_ROLLER_CONTROLS,
    H50_ROLLER_PROPERTIES,
    S40_CLASS_CONTROLS,
    S60_CLASS_STATES,
    compose_addresses,
    compose_codes,
    compose_controls,
    select_controls,
)

# Cleaning mode is the Dreame property. The water station is not published.
_OMITTED_CONTROLS: Final = frozenset(
    {
        "xiaomi_auto_water_change",
        "xiaomi_auto_water_change_installed",
        "xiaomi_base_station_tank",
        "xiaomi_cancel_water_check",
        "xiaomi_cleaning_mode",
        "xiaomi_empty_station_tank",
        "xiaomi_hot_water_wash",
        "xiaomi_spot_clean",
        "xiaomi_start_station_cleaning",
        "xiaomi_start_water_check",
        "xiaomi_use_detergent",
        "xiaomi_wash_water_temperature",
        "xiaomi_water_check_status",
    }
)
_ADDED_CONTROLS: Final = (
    *select_controls(
        EXTENDED_STATION_CONTROLS,
        (
            "xiaomi_calibrate_imu",
            "xiaomi_dust_arrest_power",
            "xiaomi_sewage_tank",
            "xiaomi_start_mop",
            "xiaomi_start_mop_wash",
            "xiaomi_station_water_level",
        ),
    ),
    *select_controls(S40_CLASS_CONTROLS, ("xiaomi_mop_auto_lift",)),
)
(_WORRY_FREE_WITH_PET,) = select_controls(
    EXTENDED_STATION_CONTROLS,
    ("xiaomi_worry_free_mode",),
)

H50_ROLLER: Final = XiaomiModel(
    model=MODEL_H50_ROLLER,
    property_overrides=compose_addresses(H50_ROLLER_PROPERTIES),
    action_overrides=compose_addresses(H50_ROLLER_ACTIONS),
    state_by_wire=compose_codes(S60_CLASS_STATES),
    task_by_wire=compose_codes(EXTENDED_STATION_TASKS),
    controls=compose_controls(
        H50_ROLLER_CONTROLS,
        _ADDED_CONTROLS,
        omitted=_OMITTED_CONTROLS,
        replaced={"xiaomi_worry_free_mode": _WORRY_FREE_WITH_PET},
    ),
)

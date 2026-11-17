"""Xiaomi Robot Vacuum 6 record composed from the station profile and roller service."""

from __future__ import annotations

from typing import Final

from .model import MODEL_ROBOT_VACUUM_6, XiaomiModel
from .profile import (
    AI_CAMERA_CONTROLS,
    EXTENDED_STATION_CONTROLS,
    EXTENDED_STATION_STATES,
    EXTENDED_STATION_TASKS,
    HOST_TANK_WITH_NOT_INSTALLED,
    ROLLER_CLEANING_MODE,
    ROLLER_CONTROLS,
    SELF_CHECK_RESULTS,
    STATION_ACTIONS,
    STATION_PROPERTIES,
    STATION_STATISTICS_PROPERTIES,
    SWEEP_DUST_ARREST,
    WORRY_FREE_THROUGH_BUTLER,
    ExtendedStationWireState,
    compose_addresses,
    compose_codes,
    compose_controls,
)

# The published spec has no mop pad, detergent consumable, hair cut, or stream.
_OMITTED_PROPERTIES: Final = frozenset(
    {
        "CLEANING_MODE",
        "MOP_PAD_LEFT",
        "MOP_PAD_TIME_LEFT",
        "DETERGENT_LEFT",
    }
)
_OMITTED_ACTIONS: Final = frozenset({"RESET_MOP_PAD", "RESET_DETERGENT"})
_OMITTED_CONTROLS: Final = frozenset(
    {
        "xiaomi_calibrate_imu",
        "xiaomi_call_clean",
        "xiaomi_carpet_deep_cleaning",
        "xiaomi_detergent_delivery",
        "xiaomi_detergent_level",
        "xiaomi_detergent_reminder",
        "xiaomi_detergent_self_delivery",
        "xiaomi_dust_arrest_power",
        "xiaomi_laser_position",
        "xiaomi_mop_water_no_tank",
        "xiaomi_obstacle_crossing",
        "xiaomi_repeat_wash_mop",
        "xiaomi_sewage_tank",
        "xiaomi_start_cut_hair",
        "xiaomi_start_eject",
        "xiaomi_start_mop",
        "xiaomi_start_mop_wash",
        "xiaomi_start_station_self_clean",
        "xiaomi_station_water_level",
        "xiaomi_stop_cut_hair",
        "xiaomi_stop_station_self_clean",
        "xiaomi_sweep_carpet_first",
    }
)
_ADDED_CONTROLS: Final = (
    ROLLER_CLEANING_MODE,
    *AI_CAMERA_CONTROLS,
    SELF_CHECK_RESULTS,
    SWEEP_DUST_ARREST,
    *ROLLER_CONTROLS,
)

ROBOT_VACUUM_6: Final = XiaomiModel(
    model=MODEL_ROBOT_VACUUM_6,
    property_overrides=compose_addresses(
        STATION_PROPERTIES,
        STATION_STATISTICS_PROPERTIES,
        omitted=_OMITTED_PROPERTIES,
    ),
    action_overrides=compose_addresses(STATION_ACTIONS, omitted=_OMITTED_ACTIONS),
    state_by_wire=compose_codes(
        EXTENDED_STATION_STATES,
        omitted=(
            int(ExtendedStationWireState.STATION_ASSISTING),
            int(ExtendedStationWireState.STATION_ASSISTED),
        ),
    ),
    task_by_wire=compose_codes(EXTENDED_STATION_TASKS),
    controls=compose_controls(
        EXTENDED_STATION_CONTROLS,
        _ADDED_CONTROLS,
        omitted=_OMITTED_CONTROLS,
        replaced={
            "xiaomi_host_tank": HOST_TANK_WITH_NOT_INSTALLED,
            "xiaomi_worry_free_mode": WORRY_FREE_THROUGH_BUTLER,
        },
    ),
)

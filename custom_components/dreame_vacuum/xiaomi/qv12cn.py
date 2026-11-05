"""Mijia Robot Vacuum 7 Max record composed from the station profile."""

from __future__ import annotations

from typing import Final

from .controls import boolean_switch, enum_select, measurement, number_control
from .model import MODEL_MIJIA_7_MAX, XiaomiModel
from .profile import (
    CAMERA_ROLLER_CONTROLS,
    CAMERA_ROLLER_OMITTED_CONTROLS,
    EXTENDED_STATION_CONTROLS,
    EXTENDED_STATION_STATES,
    EXTENDED_STATION_TASKS,
    HOST_TANK_WITH_NOT_INSTALLED,
    PRECISE_DIAGNOSIS,
    S40_CLASS_CONTROLS,
    STATION_ACTIONS,
    STATION_PROPERTIES,
    STATION_STATISTICS_PROPERTIES,
    SUMMON_STATES,
    SWEEP_SUMMON_STATES,
    WATER_LEVEL_REMIND,
    WORRY_FREE_THROUGH_BUTLER,
    ExtendedStationWireState,
    ExtendedStationWireTask,
    StationWireState,
    StationWireTask,
    SummonWireState,
    compose_addresses,
    compose_codes,
    compose_controls,
    control_with_options,
    select_controls,
)

# Preview qv12gl is not registered. This record is its future regional base.
_VACUUM_SERVICE: Final = 2
_CUSTOM_SERVICE: Final = 20
_SCREEN_SERVICE: Final = 25
_WATER_TANK_LEVEL_PROPERTY: Final = 108
_HOT_SPRAY_PROPERTY: Final = 110
_CLEAN_MODE_PROPERTY: Final = 16
_AI_IMPROVE_PROPERTY: Final = 19
_SCREEN_SWITCH_PROPERTY: Final = 1
_SCREEN_BRIGHTNESS_PROPERTY: Final = 2
_AUTO_SCREEN_OFF_PROPERTY: Final = 4
_AUTO_SCREEN_BRIGHTNESS_PROPERTY: Final = 5
_PERCENT_MINIMUM: Final = 0
_PERCENT_MAXIMUM: Final = 100
_CLEAN_MODE_GENERAL: Final = 0
_CLEAN_MODE_BUTLER: Final = 1
_CLEAN_MODE_PREFERENCE: Final = 2
_CLEAN_ONCE: Final = 1
_CLEAN_TWICE: Final = 2
_WASH_DEEP: Final = 0
_WASH_DAILY: Final = 1
_WASH_TEN_SQUARE_METERS: Final = 1
_WASH_FIFTEEN_SQUARE_METERS: Final = 3
_WASH_TWENTY_SQUARE_METERS: Final = 4
_WASH_TWENTY_FIVE_SQUARE_METERS: Final = 5

# The Dreame cleaning-mode select would write mop-only, which this spec omits.
_OMITTED_PROPERTIES: Final = frozenset({"CLEANING_MODE"})
# Station self-clean and IMU calibration are published. Hair cutting is not.
_KEPT_STATION_CONTROLS: Final = frozenset(
    {
        "xiaomi_calibrate_imu",
        "xiaomi_start_station_self_clean",
        "xiaomi_stop_station_self_clean",
    }
)
_STATION_OMITTED_CONTROLS: Final = (
    CAMERA_ROLLER_OMITTED_CONTROLS - _KEPT_STATION_CONTROLS
) | frozenset(
    {
        "xiaomi_detergent_level",
        "xiaomi_dust_bag_time_left",
        "xiaomi_laser_position",
        "xiaomi_obstacle_crossing",
        "xiaomi_repeat_wash_mop",
    }
)
_CAMERA_OMITTED_CONTROLS: Final = frozenset(
    {
        "xiaomi_enter_check_mode",
        "xiaomi_object_detection",
        "xiaomi_room_detection",
        "xiaomi_video_recording_warnings",
    }
)
_CLEAN_TIMES: Final = control_with_options(
    EXTENDED_STATION_CONTROLS,
    "xiaomi_clean_times",
    (
        (_CLEAN_ONCE, "one_time"),
        (_CLEAN_TWICE, "two_time"),
    ),
)
_WASH_WATER_OUTPUT: Final = control_with_options(
    EXTENDED_STATION_CONTROLS,
    "xiaomi_wash_water_output",
    (
        (_WASH_DEEP, "deep"),
        (_WASH_DAILY, "daily"),
    ),
)
_MOP_WASH_AREA: Final = control_with_options(
    EXTENDED_STATION_CONTROLS,
    "xiaomi_mop_wash_area",
    (
        (_WASH_TEN_SQUARE_METERS, "ten_square_meters"),
        (_WASH_FIFTEEN_SQUARE_METERS, "fifteen_square_meters"),
        (_WASH_TWENTY_SQUARE_METERS, "twenty_square_meters"),
        (_WASH_TWENTY_FIVE_SQUARE_METERS, "twenty_five_square_meters"),
    ),
)
_ADDED_CONTROLS: Final = (
    *select_controls(
        S40_CLASS_CONTROLS,
        (
            "xiaomi_ai_cleaning",
            "xiaomi_edge_swing_tail_sweep",
            "xiaomi_ai_managed_cleaning",
        ),
    ),
    measurement(
        "xiaomi_water_tank_level",
        _VACUUM_SERVICE,
        _WATER_TANK_LEVEL_PROPERTY,
        _PERCENT_MINIMUM,
        _PERCENT_MAXIMUM,
        "%",
    ),
    boolean_switch("xiaomi_hot_spray", _VACUUM_SERVICE, _HOT_SPRAY_PROPERTY),
    enum_select(
        "xiaomi_clean_mode",
        _CUSTOM_SERVICE,
        _CLEAN_MODE_PROPERTY,
        (
            (_CLEAN_MODE_GENERAL, "general"),
            (_CLEAN_MODE_BUTLER, "butler"),
            (_CLEAN_MODE_PREFERENCE, "preference"),
        ),
    ),
    boolean_switch("xiaomi_ai_improve", _CUSTOM_SERVICE, _AI_IMPROVE_PROPERTY),
    boolean_switch("xiaomi_screen", _SCREEN_SERVICE, _SCREEN_SWITCH_PROPERTY),
    number_control(
        "xiaomi_screen_brightness",
        _SCREEN_SERVICE,
        _SCREEN_BRIGHTNESS_PROPERTY,
        _PERCENT_MINIMUM,
        _PERCENT_MAXIMUM,
    ),
    boolean_switch(
        "xiaomi_auto_screen_off",
        _SCREEN_SERVICE,
        _AUTO_SCREEN_OFF_PROPERTY,
    ),
    boolean_switch(
        "xiaomi_auto_screen_brightness",
        _SCREEN_SERVICE,
        _AUTO_SCREEN_BRIGHTNESS_PROPERTY,
    ),
    PRECISE_DIAGNOSIS,
    WATER_LEVEL_REMIND,
)
_SHARED_CONTROLS: Final = compose_controls(
    EXTENDED_STATION_CONTROLS,
    CAMERA_ROLLER_CONTROLS,
    omitted=_STATION_OMITTED_CONTROLS,
    replaced={
        "xiaomi_clean_times": _CLEAN_TIMES,
        "xiaomi_host_tank": HOST_TANK_WITH_NOT_INSTALLED,
        "xiaomi_mop_wash_area": _MOP_WASH_AREA,
        "xiaomi_wash_water_output": _WASH_WATER_OUTPUT,
        "xiaomi_worry_free_mode": WORRY_FREE_THROUGH_BUTLER,
    },
)

MIJIA_7_MAX: Final = XiaomiModel(
    model=MODEL_MIJIA_7_MAX,
    property_overrides=compose_addresses(
        STATION_PROPERTIES,
        STATION_STATISTICS_PROPERTIES,
        omitted=_OMITTED_PROPERTIES,
    ),
    action_overrides=compose_addresses(STATION_ACTIONS),
    state_by_wire=compose_codes(
        EXTENDED_STATION_STATES,
        {**SUMMON_STATES, **SWEEP_SUMMON_STATES},
        omitted=(
            int(StationWireState.ERROR),
            int(StationWireState.SWEEPING_AND_MOPPING),
            int(StationWireState.MOPPING),
            int(ExtendedStationWireState.STATION_ASSISTING),
            int(ExtendedStationWireState.STATION_ASSISTED),
            int(ExtendedStationWireState.RETURNING_DURING_ASSIST),
            int(SummonWireState.SWEEP_SUMMONING),
        ),
    ),
    task_by_wire=compose_codes(
        EXTENDED_STATION_TASKS,
        omitted=(
            int(StationWireTask.EDGE),
            int(StationWireTask.CUSTOM),
            int(StationWireTask.POINT),
            int(ExtendedStationWireTask.LINKAGE),
            int(ExtendedStationWireTask.AI_HOSTING),
        ),
    ),
    controls=compose_controls(
        _SHARED_CONTROLS,
        _ADDED_CONTROLS,
        omitted=_CAMERA_OMITTED_CONTROLS,
    ),
)

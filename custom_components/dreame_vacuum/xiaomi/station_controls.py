"""Shared station controls for X20 Max-like Xiaomi models."""

from __future__ import annotations

from typing import Final

from .controls import (
    XiaomiControl,
    action_button,
    binary_reading,
    boolean_switch,
    enum_select,
    enum_sensor,
    mapped_select,
    measurement,
    number_control,
    text_sensor,
)
from .model import (
    compose_addresses,
    compose_codes,
    compose_controls,
    control_with_options,
    select_controls,
)
from .station_tables import (
    _OUTSWING_FREQUENCY_OPTIONS,
    EXTENDED_STATION_STATES,
    STATION_ACTIONS,
    STATION_PROPERTIES,
    STATION_STATISTICS_PROPERTIES,
    ExtendedStationWireState,
)

EXTENDED_STATION_CONTROLS: Final[tuple[XiaomiControl, ...]] = (
    boolean_switch("xiaomi_alarm", 4, 1),
    boolean_switch("xiaomi_carpet_avoidance", 2, 21),
    boolean_switch("xiaomi_enable_mop_wash", 2, 28),
    boolean_switch("xiaomi_auto_mop_dry", 2, 34),
    boolean_switch("xiaomi_auto_water_change", 2, 35),
    boolean_switch("xiaomi_use_detergent", 2, 36),
    boolean_switch("xiaomi_exit_remote_dialog", 2, 38),
    boolean_switch("xiaomi_hot_water_wash", 2, 41),
    boolean_switch("xiaomi_detergent_self_delivery", 2, 59),
    boolean_switch("xiaomi_detergent_reminder", 2, 71),
    boolean_switch("xiaomi_carpet_deep_cleaning", 2, 76),
    boolean_switch("xiaomi_carpet_discriminate", 2, 77),
    boolean_switch("xiaomi_sweep_carpet_first", 2, 78),
    boolean_switch("xiaomi_mop_outer_swing", 2, 79),
    boolean_switch("xiaomi_brush_outswing", 2, 91),
    boolean_switch("xiaomi_repeat_wash_mop", 2, 92),
    boolean_switch("xiaomi_detergent_delivery", 18, 2),
    enum_select(
        "xiaomi_clean_times",
        2,
        8,
        (
            (1, "one_time"),
            (2, "two_time"),
            (3, "three_time"),
        ),
    ),
    enum_select(
        "xiaomi_mop_wash_frequency",
        2,
        29,
        (
            (0, "by_room"),
            (1, "by_area"),
            (2, "by_time"),
        ),
    ),
    enum_select(
        "xiaomi_wash_water_output",
        2,
        30,
        (
            (0, "deep"),
            (1, "daily"),
            (2, "save_water"),
        ),
    ),
    enum_select(
        "xiaomi_drying_time",
        2,
        31,
        (
            (1, "hours_2"),
            (2, "hours_3"),
            (3, "hours_4"),
        ),
    ),
    enum_select(
        "xiaomi_mop_water_no_tank",
        2,
        60,
        (
            (0, "daily"),
            (1, "deep"),
        ),
    ),
    enum_select(
        "xiaomi_mop_wash_area",
        2,
        61,
        (
            (0, "five_square_meters"),
            (1, "ten_square_meters"),
            (2, "eight_square_meters"),
            (3, "fifteen_square_meters"),
            (4, "twenty_square_meters"),
            (5, "twenty_five_square_meters"),
        ),
    ),
    enum_select(
        "xiaomi_sweep_route",
        2,
        74,
        (
            (1, "quick"),
            (2, "daily"),
            (3, "careful"),
        ),
    ),
    enum_select(
        "xiaomi_obstacle_strategy",
        2,
        75,
        (
            (0, "less_collisions"),
            (1, "high_coverage"),
        ),
    ),
    enum_select(
        "xiaomi_mop_swing_frequency",
        2,
        80,
        _OUTSWING_FREQUENCY_OPTIONS,
    ),
    enum_select(
        "xiaomi_dust_arrest_power",
        2,
        82,
        (
            (0, "silent"),
            (1, "normal"),
            (2, "strong"),
        ),
    ),
    enum_select(
        "xiaomi_worry_free_mode",
        2,
        83,
        (
            (0, "silent_clean"),
            (1, "deep_clean"),
            (2, "general"),
            (3, "butler"),
            (4, "pet"),
        ),
    ),
    enum_select(
        "xiaomi_wash_water_temperature",
        2,
        84,
        (
            (0, "ordinary"),
            (1, "warm"),
            (2, "hot"),
            (3, "smart"),
        ),
    ),
    enum_select(
        "xiaomi_detergent_level",
        18,
        3,
        (
            (0, "few"),
            (1, "standard"),
            (2, "many"),
            (3, "lots"),
        ),
    ),
    enum_select(
        "xiaomi_obstacle_crossing",
        20,
        9,
        (
            (0, "safe_mode"),
            (1, "extreme_mode"),
        ),
    ),
    mapped_select(
        "xiaomi_carpet_cleaning_method",
        "CARPET_CLEANING",
        (
            (0, "self_adaption"),
            (1, "avoid"),
            (2, "ignore"),
            (3, "span"),
        ),
    ),
    number_control("xiaomi_mop_wash_interval", 2, 81, 0, 255),
    measurement("xiaomi_last_clean_time", 2, 17, 0, 4294967295),
    measurement("xiaomi_drying_progress", 2, 88, 0, 100, "%"),
    measurement("xiaomi_cleaning_progress", 2, 89, 0, 100, "%"),
    measurement("xiaomi_dry_left_time", 2, 90, 0, 9999),
    measurement("xiaomi_voltage", 3, 3, 0, 65535),
    measurement("xiaomi_download_progress", 15, 4, 0, 100, "%"),
    measurement("xiaomi_dust_bag_life", 19, 1, 0, 100, "%"),
    measurement("xiaomi_dust_bag_time_left", 19, 2, 0, 9999),
    enum_sensor(
        "xiaomi_water_check_status",
        2,
        54,
        (
            (0, "uncheck"),
            (1, "checking"),
            (2, "check_success"),
            (3, "check_fail"),
        ),
    ),
    enum_sensor(
        "xiaomi_sweep_mop_status",
        2,
        96,
        (
            (0, "idle"),
            (1, "sweeping"),
            (2, "mopping"),
        ),
    ),
    enum_sensor(
        "xiaomi_sewage_tank",
        2,
        97,
        (
            (0, "not_full"),
            (1, "full"),
        ),
    ),
    enum_sensor(
        "xiaomi_station_water_level",
        2,
        98,
        (
            (0, "not_empty"),
            (1, "empty"),
        ),
    ),
    enum_sensor(
        "xiaomi_base_station_tank",
        2,
        100,
        (
            (0, "idle"),
            (1, "emptying"),
            (2, "emptying_completed"),
            (3, "emptying_failed"),
        ),
    ),
    enum_sensor(
        "xiaomi_host_tank",
        2,
        101,
        (
            (0, "idle"),
            (1, "emptying"),
            (2, "emptying_completed"),
            (3, "emptying_failed"),
        ),
    ),
    enum_sensor(
        "xiaomi_download_status",
        15,
        3,
        (
            (0, "not_downloaded"),
            (1, "downloading"),
            (2, "downloaded"),
            (3, "download_fail"),
            (4, "apply_success"),
            (5, "apply_fail"),
        ),
    ),
    enum_sensor(
        "xiaomi_laser_position",
        20,
        11,
        (
            (0, "bottom"),
            (1, "top"),
            (2, "lifting"),
            (3, "lowering"),
        ),
    ),
    text_sensor("xiaomi_base_station_status", 2, 18),
    text_sensor("xiaomi_notice", 2, 72),
    text_sensor("xiaomi_current_voice", 15, 2),
    binary_reading("xiaomi_sleep_status", 2, 25),
    binary_reading("xiaomi_auto_water_change_installed", 2, 62),
    binary_reading("xiaomi_current_child_lock", 5, 2),
    binary_reading("xiaomi_current_dnd", 11, 3),
    action_button("xiaomi_stop_and_charge", 2, 3),
    action_button("xiaomi_start_sweep", 2, 4),
    action_button("xiaomi_start_mop", 2, 5),
    action_button("xiaomi_start_sweep_mop", 2, 6),
    action_button("xiaomi_start_mop_wash", 2, 19),
    action_button("xiaomi_start_dry", 2, 20),
    action_button("xiaomi_start_eject", 2, 21),
    action_button("xiaomi_call_clean", 2, 22),
    action_button("xiaomi_try_listen", 2, 27),
    action_button("xiaomi_enter_remote", 2, 28),
    action_button("xiaomi_exit_remote", 2, 29),
    action_button("xiaomi_stop_mop_wash", 2, 31),
    action_button("xiaomi_stop_dry", 2, 32),
    action_button("xiaomi_back_to_wash", 2, 36),
    action_button("xiaomi_start_cut_hair", 2, 43),
    action_button("xiaomi_stop_cut_hair", 2, 44),
    action_button("xiaomi_start_water_check", 2, 45),
    action_button("xiaomi_cancel_water_check", 2, 46),
    action_button("xiaomi_start_station_cleaning", 2, 49),
    action_button("xiaomi_sweep_before_mop", 2, 50),
    action_button("xiaomi_stop_working", 2, 51),
    action_button("xiaomi_empty_station_tank", 2, 57),
    action_button("xiaomi_empty_host_tank", 2, 58),
    action_button("xiaomi_spot_clean", 2, 59),
    action_button("xiaomi_start_station_self_clean", 2, 63),
    action_button("xiaomi_stop_station_self_clean", 2, 64),
    action_button("xiaomi_calibrate_imu", 16, 1),
    action_button("xiaomi_reset_dust_bag", 19, 1),
)

# The shared list also publishes Pet.
WORRY_FREE_THROUGH_BUTLER: Final = control_with_options(
    EXTENDED_STATION_CONTROLS,
    "xiaomi_worry_free_mode",
    (
        (0, "silent_clean"),
        (1, "deep_clean"),
        (2, "general"),
        (3, "butler"),
    ),
)

_DRYING_TWO_HOURS: Final = 1
_DRYING_THREE_HOURS: Final = 2
_DRYING_FOUR_HOURS: Final = 3
_DRYING_FIVE_HOURS: Final = 4
_DRYING_SIX_HOURS: Final = 5
_DRYING_SEVEN_HOURS: Final = 6
_DRYING_EIGHT_HOURS: Final = 7
_DRYING_NINE_HOURS: Final = 8
_DRYING_TEN_HOURS: Final = 9
_DRYING_ELEVEN_HOURS: Final = 10
_DRYING_TWELVE_HOURS: Final = 11

# H50 and Mijia H40 publish drying time through 12 hours.
DRYING_TIME_THROUGH_TWELVE_HOURS: Final = control_with_options(
    EXTENDED_STATION_CONTROLS,
    "xiaomi_drying_time",
    (
        (_DRYING_TWO_HOURS, "hours_2"),
        (_DRYING_THREE_HOURS, "hours_3"),
        (_DRYING_FOUR_HOURS, "hours_4"),
        (_DRYING_FIVE_HOURS, "hours_5"),
        (_DRYING_SIX_HOURS, "hours_6"),
        (_DRYING_SEVEN_HOURS, "hours_7"),
        (_DRYING_EIGHT_HOURS, "hours_8"),
        (_DRYING_NINE_HOURS, "hours_9"),
        (_DRYING_TEN_HOURS, "hours_10"),
        (_DRYING_ELEVEN_HOURS, "hours_11"),
        (_DRYING_TWELVE_HOURS, "hours_12"),
    ),
)

# The shared list stops at emptying failed.
HOST_TANK_WITH_NOT_INSTALLED: Final = control_with_options(
    EXTENDED_STATION_CONTROLS,
    "xiaomi_host_tank",
    (
        (0, "idle"),
        (1, "emptying"),
        (2, "emptying_completed"),
        (3, "emptying_failed"),
        (4, "not_installed"),
    ),
)

HAIR_CUTTING_CONTROLS: Final[tuple[XiaomiControl, ...]] = (
    boolean_switch("xiaomi_cut_hair", 2, 63),
    enum_select(
        "xiaomi_cut_hair_frequency",
        2,
        64,
        (
            (1, "every_clean"),
            (2, "every_two_cleans"),
            (3, "every_three_cleans"),
            (4, "during_task"),
        ),
    ),
)

# Shared by the S40-class spec. H40 lacks detergent reminder 2.71, which stays
# on the extended list so that model omits xiaomi_detergent_reminder.
_SWEEP_AI_DETECTION: Final = boolean_switch("xiaomi_sweep_ai_detection", 2, 45)
_EDGE_SWEEP_FREQUENCY: Final = enum_select(
    "xiaomi_edge_sweep_frequency",
    2,
    68,
    _OUTSWING_FREQUENCY_OPTIONS,
)

# Robot Vacuum 6 publishes only these two from the S40-class camera list.
AI_CAMERA_CONTROLS: Final[tuple[XiaomiControl, ...]] = (
    _SWEEP_AI_DETECTION,
    _EDGE_SWEEP_FREQUENCY,
)

_S40_CLASS_ONLY_CONTROLS: Final[tuple[XiaomiControl, ...]] = (
    boolean_switch("xiaomi_ai_cleaning", 2, 37),
    boolean_switch("xiaomi_mop_auto_lift", 2, 44),
    _SWEEP_AI_DETECTION,
    boolean_switch("xiaomi_dirt_detection", 2, 46),
    boolean_switch("xiaomi_object_detection", 2, 47),
    boolean_switch("xiaomi_room_detection", 2, 48),
    boolean_switch("xiaomi_floor_material_detection", 2, 49),
    boolean_switch("xiaomi_defecation_detection", 2, 50),
    boolean_switch("xiaomi_liquid_dirt_detection", 2, 51),
    boolean_switch("xiaomi_edge_swing_tail_sweep", 2, 55),
    _EDGE_SWEEP_FREQUENCY,
    boolean_switch("xiaomi_ai_managed_cleaning", 2, 69),
    boolean_switch("xiaomi_real_scene_capture", 2, 93),
    boolean_switch("xiaomi_auto_night_fill_light", 2, 94),
    boolean_switch("xiaomi_ai_wake_up", 2, 95),
)

S40_CLASS_CONTROLS: Final[tuple[XiaomiControl, ...]] = (
    *HAIR_CUTTING_CONTROLS,
    *_S40_CLASS_ONLY_CONTROLS,
)

# H50, H50 Pro, and Robot Vacuum 5 Pro publish this. The S40 spec does not.
SOLID_DIRT_DETECTION: Final = boolean_switch("xiaomi_solid_dirt_detection", 2, 52)

# Robot Vacuum 5 Pro publishes these. H50 and H50 Pro leave them unmapped.
LIDAR_HARDWARE_CONTROLS: Final[frozenset[str]] = frozenset(
    {
        "xiaomi_laser_position",
        "xiaomi_obstacle_crossing",
    }
)

_STREAM_SERVICE: Final = 21
_FLASH_LIGHT_PROPERTY: Final = 2
_PET_SNAPS_PROPERTY: Final = 3
_VIDEO_WARNING_PROPERTY: Final = 4
_SHARED_USERS_PROPERTY: Final = 5
_STREAM_ENABLED_PROPERTY: Final = 6
_STREAM_LOCK_PROPERTY: Final = 8
_FIND_PET_ACTION: Final = 3

# Robot Vacuum 5 Pro and H50 publish camera cruise and pet finding.
STREAM_CONTROLS: Final[tuple[XiaomiControl, ...]] = (
    enum_select(
        "xiaomi_flash_light",
        _STREAM_SERVICE,
        _FLASH_LIGHT_PROPERTY,
        (
            (0, "auto"),
            (1, "open"),
            (2, "close"),
        ),
    ),
    boolean_switch("xiaomi_pet_snaps", _STREAM_SERVICE, _PET_SNAPS_PROPERTY),
    enum_select(
        "xiaomi_video_recording_warnings",
        _STREAM_SERVICE,
        _VIDEO_WARNING_PROPERTY,
        (
            (0, "voice"),
            (1, "light"),
            (2, "strong_reminder"),
        ),
    ),
    boolean_switch(
        "xiaomi_stream_visible_to_shared_users",
        _STREAM_SERVICE,
        _SHARED_USERS_PROPERTY,
    ),
    boolean_switch("xiaomi_stream_enabled", _STREAM_SERVICE, _STREAM_ENABLED_PROPERTY),
    binary_reading(
        "xiaomi_stream_physical_lock", _STREAM_SERVICE, _STREAM_LOCK_PROPERTY
    ),
    action_button("xiaomi_find_pet", _STREAM_SERVICE, _FIND_PET_ACTION),
)

_SELF_CHECK_SERVICE: Final = 22
_SELF_CHECK_RESULTS_PROPERTY: Final = 2

# H50 Pro and H50 publish this readable string in spec version 2.
SELF_CHECK_RESULTS: Final = text_sensor(
    "xiaomi_self_check_results",
    _SELF_CHECK_SERVICE,
    _SELF_CHECK_RESULTS_PROPERTY,
)

_VACUUM_SERVICE: Final = 2
_CLEANING_MODE_PROPERTY: Final = 4
_MOP_TEMPERATURE_PROPERTY: Final = 107

# The Dreame select would send mop-only, which these specs do not publish.
ROLLER_CLEANING_MODE: Final = enum_select(
    "xiaomi_cleaning_mode",
    _VACUUM_SERVICE,
    _CLEANING_MODE_PROPERTY,
    (
        (1, "sweeping"),
        (3, "sweeping_and_mopping"),
        (4, "mopping_after_sweeping"),
    ),
)

_ROLLER_SERVICE: Final = 24
_ROLLER_LIFE_PROPERTY: Final = 1
_ROLLER_TIME_PROPERTY: Final = 2
_ROLLER_OUTSWING_PROPERTY: Final = 3
_ROLLER_AUTO_WASH_PROPERTY: Final = 4
_RESET_ROLLER_ACTION: Final = 1
_START_ROLLER_WASH_ACTION: Final = 2
_STOP_ROLLER_WASH_ACTION: Final = 3

# Robot Vacuum 6 mops with a roller. It does not publish mop-pad life.
ROLLER_CONTROLS: Final[tuple[XiaomiControl, ...]] = (
    measurement(
        "xiaomi_roller_life",
        _ROLLER_SERVICE,
        _ROLLER_LIFE_PROPERTY,
        0,
        100,
        "%",
    ),
    measurement(
        "xiaomi_roller_time_left",
        _ROLLER_SERVICE,
        _ROLLER_TIME_PROPERTY,
        0,
        9999,
    ),
    boolean_switch(
        "xiaomi_roller_outswing",
        _ROLLER_SERVICE,
        _ROLLER_OUTSWING_PROPERTY,
    ),
    boolean_switch(
        "xiaomi_auto_wash_roller",
        _ROLLER_SERVICE,
        _ROLLER_AUTO_WASH_PROPERTY,
    ),
    action_button("xiaomi_reset_roller", _ROLLER_SERVICE, _RESET_ROLLER_ACTION),
    action_button(
        "xiaomi_start_roller_wash",
        _ROLLER_SERVICE,
        _START_ROLLER_WASH_ACTION,
    ),
    action_button(
        "xiaomi_stop_roller_wash",
        _ROLLER_SERVICE,
        _STOP_ROLLER_WASH_ACTION,
    ),
)

_CUSTOM_SERVICE: Final = 20
_SWEEP_DUST_ARREST_ACTION: Final = 9
_ENTER_CHECK_MODE_ACTION: Final = 11

# Dust collection during a clean. Start-dust-arrest remains the dock empty.
SWEEP_DUST_ARREST: Final = action_button(
    "xiaomi_sweep_dust_arrest",
    _CUSTOM_SERVICE,
    _SWEEP_DUST_ARREST_ACTION,
)

# A parameter-free self-check entry. The result string is a separate sensor.
ENTER_CHECK_MODE: Final = action_button(
    "xiaomi_enter_check_mode",
    _CUSTOM_SERVICE,
    _ENTER_CHECK_MODE_ACTION,
)

# Device mop-water temperature. It is not the per-room Dreame mop-temperature map.
MOP_TEMPERATURE: Final = enum_select(
    "xiaomi_mop_temperature",
    _VACUUM_SERVICE,
    _MOP_TEMPERATURE_PROPERTY,
    (
        (0, "normal"),
        (1, "warm"),
        (2, "hot"),
        (3, "smart"),
    ),
)

_CAMERA_ROLLER_DETECTION_KEYS: Final = (
    "xiaomi_mop_auto_lift",
    "xiaomi_sweep_ai_detection",
    "xiaomi_dirt_detection",
    "xiaomi_object_detection",
    "xiaomi_room_detection",
    "xiaomi_edge_sweep_frequency",
    "xiaomi_real_scene_capture",
    "xiaomi_auto_night_fill_light",
    "xiaomi_ai_wake_up",
)
_CAMERA_ROLLER_STREAM_KEYS: Final = (
    "xiaomi_flash_light",
    "xiaomi_video_recording_warnings",
    "xiaomi_stream_visible_to_shared_users",
    "xiaomi_stream_enabled",
    "xiaomi_stream_physical_lock",
)

# Robot Vacuum 6 Max and 6 Pro add this camera, stream, and roller set.
CAMERA_ROLLER_CONTROLS: Final[tuple[XiaomiControl, ...]] = (
    ROLLER_CLEANING_MODE,
    *select_controls(S40_CLASS_CONTROLS, _CAMERA_ROLLER_DETECTION_KEYS),
    SELF_CHECK_RESULTS,
    SWEEP_DUST_ARREST,
    *ROLLER_CONTROLS,
    *select_controls(STREAM_CONTROLS, _CAMERA_ROLLER_STREAM_KEYS),
    MOP_TEMPERATURE,
    ENTER_CHECK_MODE,
)

# These shared-list addresses are absent from both of those specs.
CAMERA_ROLLER_OMITTED_CONTROLS: Final[frozenset[str]] = frozenset(
    {
        "xiaomi_calibrate_imu",
        "xiaomi_dust_arrest_power",
        "xiaomi_start_cut_hair",
        "xiaomi_start_mop",
        "xiaomi_start_station_self_clean",
        "xiaomi_stop_cut_hair",
        "xiaomi_stop_station_self_clean",
    }
)

_VIBRATION_MOP_PROPERTY: Final = 109

# Both S60 models publish a vibrating mop pad. It is not a roller wash switch.
VIBRATION_MOP: Final = boolean_switch(
    "xiaomi_vibration_mop",
    _VACUUM_SERVICE,
    _VIBRATION_MOP_PROPERTY,
)

# Pad-mop slice both S60 models publish. Wash, roller, and stream services are empty.
_S60_CLASS_CONTROL_KEYS: Final = (
    "xiaomi_alarm",
    "xiaomi_carpet_avoidance",
    "xiaomi_exit_remote_dialog",
    "xiaomi_carpet_deep_cleaning",
    "xiaomi_carpet_discriminate",
    "xiaomi_sweep_carpet_first",
    "xiaomi_clean_times",
    "xiaomi_sweep_route",
    "xiaomi_worry_free_mode",
    "xiaomi_carpet_cleaning_method",
    "xiaomi_last_clean_time",
    "xiaomi_cleaning_progress",
    "xiaomi_voltage",
    "xiaomi_download_progress",
    "xiaomi_sweep_mop_status",
    "xiaomi_download_status",
    "xiaomi_base_station_status",
    "xiaomi_notice",
    "xiaomi_current_voice",
    "xiaomi_sleep_status",
    "xiaomi_current_child_lock",
    "xiaomi_current_dnd",
    "xiaomi_stop_and_charge",
    "xiaomi_start_sweep",
    "xiaomi_start_mop",
    "xiaomi_start_sweep_mop",
    "xiaomi_try_listen",
    "xiaomi_enter_remote",
    "xiaomi_exit_remote",
    "xiaomi_sweep_before_mop",
    "xiaomi_stop_working",
    "xiaomi_calibrate_imu",
)
S60_CLASS_CONTROLS: Final[tuple[XiaomiControl, ...]] = (
    *select_controls(EXTENDED_STATION_CONTROLS, _S60_CLASS_CONTROL_KEYS),
    *select_controls(S40_CLASS_CONTROLS, ("xiaomi_edge_sweep_frequency",)),
    SELF_CHECK_RESULTS,
    VIBRATION_MOP,
)

# Extended-station controls whose addresses the S40-class spec does not publish.
S40_CLASS_OMITTED_CONTROLS: Final[frozenset[str]] = frozenset(
    {
        "xiaomi_carpet_deep_cleaning",
        "xiaomi_carpet_discriminate",
        "xiaomi_laser_position",
        "xiaomi_mop_outer_swing",
        "xiaomi_mop_swing_frequency",
        "xiaomi_mop_wash_frequency",
        "xiaomi_mop_wash_interval",
        "xiaomi_obstacle_crossing",
        "xiaomi_sweep_carpet_first",
    }
)

# Neither roller spec publishes a mop pad or a detergent consumable.
_H50_ROLLER_OMITTED_PROPERTIES: Final[frozenset[str]] = frozenset(
    {
        "DETERGENT_LEFT",
        "MOP_PAD_LEFT",
        "MOP_PAD_TIME_LEFT",
    }
)
_H50_ROLLER_OMITTED_ACTIONS: Final[frozenset[str]] = frozenset(
    {"RESET_DETERGENT", "RESET_MOP_PAD"}
)
# Dropped from the shared list when either roller spec leaves the address out.
_H50_ROLLER_OMITTED_CONTROLS: Final[frozenset[str]] = frozenset(
    {
        "xiaomi_brush_outswing",
        "xiaomi_calibrate_imu",
        "xiaomi_call_clean",
        "xiaomi_detergent_delivery",
        "xiaomi_detergent_level",
        "xiaomi_detergent_reminder",
        "xiaomi_detergent_self_delivery",
        "xiaomi_dust_arrest_power",
        "xiaomi_laser_position",
        "xiaomi_mop_outer_swing",
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
    }
)
H50_ROLLER_PROPERTIES: Final[dict[str, dict[str, int]]] = compose_addresses(
    STATION_PROPERTIES,
    STATION_STATISTICS_PROPERTIES,
    omitted=_H50_ROLLER_OMITTED_PROPERTIES,
)
H50_ROLLER_ACTIONS: Final[dict[str, dict[str, int]]] = compose_addresses(
    STATION_ACTIONS,
    omitted=_H50_ROLLER_OMITTED_ACTIONS,
)
# Status skips station-assist 22 and 23. Wire 24 is still returning.
H50_ROLLER_STATES: Final[dict[int, int]] = compose_codes(
    EXTENDED_STATION_STATES,
    omitted=(
        int(ExtendedStationWireState.STATION_ASSISTING),
        int(ExtendedStationWireState.STATION_ASSISTED),
    ),
)
H50_ROLLER_CONTROLS: Final[tuple[XiaomiControl, ...]] = compose_controls(
    EXTENDED_STATION_CONTROLS,
    (
        ROLLER_CLEANING_MODE,
        *select_controls(AI_CAMERA_CONTROLS, ("xiaomi_edge_sweep_frequency",)),
        SELF_CHECK_RESULTS,
        SWEEP_DUST_ARREST,
        *ROLLER_CONTROLS,
    ),
    omitted=_H50_ROLLER_OMITTED_CONTROLS,
    replaced={
        "xiaomi_host_tank": HOST_TANK_WITH_NOT_INSTALLED,
        "xiaomi_worry_free_mode": WORRY_FREE_THROUGH_BUTLER,
    },
)

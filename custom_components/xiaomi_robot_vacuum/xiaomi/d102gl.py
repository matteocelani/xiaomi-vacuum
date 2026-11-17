"""Xiaomi X20 Pro model record composed from the station profile."""

from __future__ import annotations

from typing import Final

from .model import MODEL_X20_PRO, XiaomiModel
from .profile import (
    EXTENDED_STATION_CONTROLS,
    EXTENDED_STATION_STATES,
    S40_CLASS_CONTROLS,
    STATION_ACTIONS,
    STATION_PROPERTIES,
    STATION_TASKS,
    ExtendedStationWireState,
    compose_addresses,
    compose_codes,
    compose_controls,
    control_with_options,
    select_controls,
)

# These extended-station addresses are not in the released spec.
_OMITTED_CONTROLS: Final = frozenset(
    {
        "xiaomi_base_station_tank",
        "xiaomi_brush_outswing",
        "xiaomi_calibrate_imu",
        "xiaomi_call_clean",
        "xiaomi_cleaning_progress",
        "xiaomi_dry_left_time",
        "xiaomi_drying_progress",
        "xiaomi_dust_arrest_power",
        "xiaomi_empty_host_tank",
        "xiaomi_empty_station_tank",
        "xiaomi_host_tank",
        "xiaomi_hot_water_wash",
        "xiaomi_laser_position",
        "xiaomi_mop_outer_swing",
        "xiaomi_mop_swing_frequency",
        "xiaomi_mop_wash_interval",
        "xiaomi_obstacle_crossing",
        "xiaomi_repeat_wash_mop",
        "xiaomi_sewage_tank",
        "xiaomi_spot_clean",
        "xiaomi_start_cut_hair",
        "xiaomi_start_station_cleaning",
        "xiaomi_start_station_self_clean",
        "xiaomi_station_water_level",
        "xiaomi_stop_cut_hair",
        "xiaomi_stop_station_self_clean",
        "xiaomi_stop_working",
        "xiaomi_sweep_before_mop",
        "xiaomi_sweep_mop_status",
        "xiaomi_wash_water_temperature",
        "xiaomi_worry_free_mode",
    }
)

# The shared list continues through twenty-five square meters.
_MOP_WASH_AREA: Final = control_with_options(
    EXTENDED_STATION_CONTROLS,
    "xiaomi_mop_wash_area",
    (
        (0, "five_square_meters"),
        (1, "ten_square_meters"),
        (2, "eight_square_meters"),
    ),
)

# Wire 1 is every time here. The S40-class list publishes the opposite order.
_EDGE_SWEEP_FREQUENCY: Final = control_with_options(
    S40_CLASS_CONTROLS,
    "xiaomi_edge_sweep_frequency",
    (
        (1, "every_time"),
        (2, "seven_sweeps"),
    ),
)

_ADDED_CONTROLS: Final = (
    *select_controls(S40_CLASS_CONTROLS, ("xiaomi_edge_swing_tail_sweep",)),
    _EDGE_SWEEP_FREQUENCY,
)

# Status stops at 21. Remote stays on the old code so the shell can label it.
_OMITTED_STATES: Final = (
    int(ExtendedStationWireState.STATION_ASSISTING),
    int(ExtendedStationWireState.STATION_ASSISTED),
    int(ExtendedStationWireState.RETURNING_DURING_ASSIST),
)

X20_PRO: Final = XiaomiModel(
    model=MODEL_X20_PRO,
    property_overrides=compose_addresses(STATION_PROPERTIES),
    action_overrides=compose_addresses(STATION_ACTIONS),
    state_by_wire=compose_codes(EXTENDED_STATION_STATES, omitted=_OMITTED_STATES),
    task_by_wire=compose_codes(STATION_TASKS),
    controls=compose_controls(
        EXTENDED_STATION_CONTROLS,
        _ADDED_CONTROLS,
        omitted=_OMITTED_CONTROLS,
        replaced={"xiaomi_mop_wash_area": _MOP_WASH_AREA},
    ),
)

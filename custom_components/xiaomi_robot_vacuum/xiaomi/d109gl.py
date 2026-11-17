"""Xiaomi X20 Max model record composed from the station profile."""

from __future__ import annotations

from typing import Final

from .model import MODEL_X20_MAX, XiaomiModel
from .profile import (
    EXTENDED_STATION_CONTROLS,
    STATION_ACTIONS,
    STATION_PROPERTIES,
    STATION_STATES,
    STATION_TASKS,
    compose_addresses,
    compose_codes,
    compose_controls,
    control_with_options,
    select_controls,
)

# Addresses the d109gl spec publishes. Worry-free and mop-swing are replaced below.
_STATION_KEYS: Final[tuple[str, ...]] = (
    "xiaomi_clean_times",
    "xiaomi_carpet_avoidance",
    "xiaomi_enable_mop_wash",
    "xiaomi_mop_wash_frequency",
    "xiaomi_wash_water_output",
    "xiaomi_drying_time",
    "xiaomi_auto_mop_dry",
    "xiaomi_auto_water_change",
    "xiaomi_use_detergent",
    "xiaomi_detergent_self_delivery",
    "xiaomi_mop_water_no_tank",
    "xiaomi_mop_wash_area",
    "xiaomi_detergent_reminder",
    "xiaomi_sweep_route",
    "xiaomi_obstacle_strategy",
    "xiaomi_carpet_deep_cleaning",
    "xiaomi_carpet_discriminate",
    "xiaomi_sweep_carpet_first",
    "xiaomi_mop_outer_swing",
    "xiaomi_mop_swing_frequency",
    "xiaomi_mop_wash_interval",
    "xiaomi_dust_arrest_power",
    "xiaomi_worry_free_mode",
    "xiaomi_wash_water_temperature",
    "xiaomi_alarm",
    "xiaomi_detergent_delivery",
    "xiaomi_detergent_level",
)
_SHARED: Final = select_controls(EXTENDED_STATION_CONTROLS, _STATION_KEYS)
# Spec order is Every Time then 7 Sweeps. The shared tuple swaps those labels.
_MOP_SWING: Final = control_with_options(
    _SHARED,
    "xiaomi_mop_swing_frequency",
    ((1, "every_time"), (2, "seven_sweeps")),
)
# This spec stops at Standard. Butler and pet are not published.
_WORRY_FREE: Final = control_with_options(
    _SHARED,
    "xiaomi_worry_free_mode",
    ((0, "silent_clean"), (1, "deep_clean"), (2, "general")),
)

X20_MAX: Final = XiaomiModel(
    model=MODEL_X20_MAX,
    property_overrides=compose_addresses(STATION_PROPERTIES),
    action_overrides=compose_addresses(STATION_ACTIONS),
    state_by_wire=compose_codes(STATION_STATES),
    task_by_wire=compose_codes(STATION_TASKS),
    controls=compose_controls(
        _SHARED,
        replaced={
            "xiaomi_mop_swing_frequency": _MOP_SWING,
            "xiaomi_worry_free_mode": _WORRY_FREE,
        },
    ),
)

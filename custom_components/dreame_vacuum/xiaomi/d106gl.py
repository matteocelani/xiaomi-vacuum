"""Xiaomi Robot Vacuum S20 record on the sweep spec family."""

from __future__ import annotations

from enum import IntEnum
from typing import Final

from .controls import (
    XiaomiControl,
    action_button,
    boolean_switch,
    enum_select,
)
from .model import (
    MODEL_S20,
    StoredState,
    XiaomiModel,
    compose_addresses,
    compose_codes,
    compose_controls,
    control_with_options,
)
from .sweep import (
    CARPET_AVOID,
    MOP_AVOID,
    REMEMBER_MAP,
    SWEEP_ACTIONS,
    SWEEP_AVOID,
    SWEEP_CONTROLS,
    SWEEP_PROPERTIES,
    SWEEP_STATES,
)

_CLOSE_OPEN: Final[tuple[tuple[int, str], ...]] = (
    (0, "close"),
    (1, "open"),
)
# The spec spells the high water step Hig.
_WATER_OPTIONS: Final[tuple[tuple[int, str], ...]] = (
    (0, "low"),
    (1, "mid"),
    (2, "high"),
)
# Index 3 is the filter and 4 is the cloth. The shared buttons send 4 and 8.
_CONSUMABLE_INDEX: Final = 17
_FILTER_CONSUMABLE: Final = 3
_CLOTH_CONSUMABLE: Final = 4
_RESET_FILTER: Final = action_button(
    "xiaomi_reset_filter",
    7,
    1,
    ((_CONSUMABLE_INDEX, _FILTER_CONSUMABLE),),
)
_RESET_MOP: Final = action_button(
    "xiaomi_reset_mop",
    7,
    1,
    ((_CONSUMABLE_INDEX, _CLOTH_CONSUMABLE),),
)
# The released alarm is a boolean. The shared list is a one-value play enum.
_ALARM: Final = boolean_switch("xiaomi_alarm", 4, 1)
_ADDED_CONTROLS: Final[tuple[XiaomiControl, ...]] = (
    enum_select(
        "xiaomi_suction_level",
        2,
        11,
        (
            (0, "silent"),
            (1, "basic"),
            (2, "strong"),
            (3, "full_speed"),
        ),
    ),
    enum_select("xiaomi_dirt_recognition", 7, 35, _CLOSE_OPEN),
    enum_select("xiaomi_pet_recognition", 7, 36, _CLOSE_OPEN),
    enum_select("xiaomi_ai_recognition", 7, 42, _CLOSE_OPEN),
    enum_select("xiaomi_carpet_boost", 7, 44, _CLOSE_OPEN),
    enum_select("xiaomi_tank_shake", 7, 48, _CLOSE_OPEN),
    enum_select("xiaomi_electrolysis", 7, 49, _CLOSE_OPEN),
    enum_select(
        "xiaomi_mop_shake",
        7,
        50,
        (
            (1, "low"),
            (2, "mid"),
            (3, "high"),
        ),
    ),
    CARPET_AVOID,
    SWEEP_AVOID,
    MOP_AVOID,
    REMEMBER_MAP,
)


class _ExtraWireState(IntEnum):
    """Status codes the S20 spec adds after the shared sweep list."""

    BUILDING = 9
    CHARGING = 10


S20: Final = XiaomiModel(
    model=MODEL_S20,
    property_overrides=compose_addresses(SWEEP_PROPERTIES),
    action_overrides=compose_addresses(SWEEP_ACTIONS),
    state_by_wire=compose_codes(
        SWEEP_STATES,
        {
            int(_ExtraWireState.BUILDING): int(StoredState.BUILDING),
            int(_ExtraWireState.CHARGING): int(StoredState.CHARGING),
        },
    ),
    task_by_wire={},
    controls=compose_controls(
        SWEEP_CONTROLS,
        _ADDED_CONTROLS,
        replaced={
            "xiaomi_alarm": _ALARM,
            "xiaomi_mop_route": control_with_options(
                SWEEP_CONTROLS,
                "xiaomi_mop_route",
                (
                    (0, "s_shape"),
                    (1, "y_shape"),
                ),
            ),
            "xiaomi_repeat_clean": control_with_options(
                SWEEP_CONTROLS,
                "xiaomi_repeat_clean",
                _CLOSE_OPEN,
            ),
            "xiaomi_reset_filter": _RESET_FILTER,
            "xiaomi_reset_mop": _RESET_MOP,
            "xiaomi_suction": control_with_options(
                SWEEP_CONTROLS,
                "xiaomi_suction",
                (
                    (0, "silent"),
                    (1, "standard"),
                    (2, "medium"),
                    (3, "turbo"),
                ),
            ),
            "xiaomi_sweep_mode": control_with_options(
                SWEEP_CONTROLS,
                "xiaomi_sweep_mode",
                (
                    (0, "sweep"),
                    (1, "sweep_and_mop"),
                    (2, "mop"),
                    (3, "sweep_then_mop"),
                ),
            ),
            "xiaomi_sweep_type": control_with_options(
                SWEEP_CONTROLS,
                "xiaomi_sweep_type",
                (
                    (0, "global"),
                    (1, "mop"),
                    (2, "edge"),
                    (3, "area"),
                    (4, "point"),
                    (5, "remote"),
                    (6, "explore"),
                    (7, "room"),
                    (8, "floor"),
                ),
            ),
            "xiaomi_water_level": control_with_options(
                SWEEP_CONTROLS,
                "xiaomi_water_level",
                _WATER_OPTIONS,
            ),
        },
    ),
)

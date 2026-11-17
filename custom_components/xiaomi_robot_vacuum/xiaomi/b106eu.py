"""Xiaomi Robot Vacuum S12 record on the sweep spec family."""

from __future__ import annotations

from dataclasses import replace
from enum import IntEnum
from typing import Final

from .controls import (
    XiaomiControl,
    action_button,
    boolean_switch,
    enum_select,
)
from .model import (
    MODEL_S12,
    MODEL_T12,
    StoredState,
    XiaomiModel,
    compose_addresses,
    compose_codes,
    compose_controls,
    control_with_options,
)
from .sweep import (
    CARPET_AVOID,
    REMEMBER_MAP,
    SWEEP_ACTIONS,
    SWEEP_CONTROLS,
    SWEEP_PROPERTIES,
    SWEEP_STATES,
)

_CLOSE_OPEN: Final[tuple[tuple[int, str], ...]] = (
    (0, "close"),
    (1, "open"),
)
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
# The spec spells manual control Man.
_SWEEP_TYPE_OPTIONS: Final[tuple[tuple[int, str], ...]] = (
    (0, "global"),
    (1, "mop"),
    (2, "corner"),
    (3, "area"),
    (4, "point"),
    (5, "manual"),
    (6, "explore"),
    (7, "room_prefer"),
    (8, "material_prefer"),
)
# The spec spells the quiet suction step Slient.
_SUCTION_OPTIONS: Final[tuple[tuple[int, str], ...]] = (
    (0, "silent"),
    (1, "standard"),
    (2, "medium"),
    (3, "turbo"),
)
_ADDED_CONTROLS: Final[tuple[XiaomiControl, ...]] = (
    enum_select("xiaomi_dirt_recognition", 7, 35, _CLOSE_OPEN),
    enum_select("xiaomi_pet_recognition", 7, 36, _CLOSE_OPEN),
    enum_select("xiaomi_ai_recognition", 7, 42, _CLOSE_OPEN),
    enum_select("xiaomi_carpet_boost", 7, 44, _CLOSE_OPEN),
    enum_select("xiaomi_tank_shake", 7, 48, _CLOSE_OPEN),
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
    REMEMBER_MAP,
)


class _StatusWire(IntEnum):
    """Status wires whose meaning differs from the shared sweep list."""

    MOPPING = 6
    SWEEPING_AND_MOPPING = 7


S12: Final = XiaomiModel(
    model=MODEL_S12,
    property_overrides=compose_addresses(SWEEP_PROPERTIES),
    action_overrides=compose_addresses(SWEEP_ACTIONS),
    # Released status swaps mopping with sweeping-and-mopping.
    state_by_wire=compose_codes(
        SWEEP_STATES,
        {
            int(_StatusWire.MOPPING): int(StoredState.MOPPING),
            int(_StatusWire.SWEEPING_AND_MOPPING): int(
                StoredState.SWEEPING_AND_MOPPING
            ),
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
                _SUCTION_OPTIONS,
            ),
            "xiaomi_sweep_mode": control_with_options(
                SWEEP_CONTROLS,
                "xiaomi_sweep_mode",
                (
                    (0, "sweep"),
                    (1, "sweep_and_mop"),
                    (2, "mop"),
                ),
            ),
            "xiaomi_sweep_type": control_with_options(
                SWEEP_CONTROLS,
                "xiaomi_sweep_type",
                _SWEEP_TYPE_OPTIONS,
            ),
            "xiaomi_water_level": control_with_options(
                SWEEP_CONTROLS,
                "xiaomi_water_level",
                _WATER_OPTIONS,
            ),
        },
    ),
)
# Released T12 matches S12, so it reuses this record.
T12: Final = replace(S12, model=MODEL_T12)

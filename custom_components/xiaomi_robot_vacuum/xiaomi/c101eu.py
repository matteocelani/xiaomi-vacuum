"""Xiaomi Robot Vacuum X20 record on the sweep spec family."""

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
    MODEL_X20,
    StoredState,
    XiaomiModel,
    compose_addresses,
    compose_codes,
    compose_controls,
    control_with_options,
)
from .sweep import (
    BACK_WASH_AREA,
    CARPET_AVOID,
    DRY_TIME,
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
# Shell codes above 18 pass through the old state enum while new_state is off.
_LEGACY_AUTO_EMPTYING: Final = 24
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
    enum_select(
        "xiaomi_air_dry",
        7,
        54,
        (
            (0, "pause"),
            (1, "start"),
        ),
    ),
    enum_select("xiaomi_child_lock", 7, 59, _CLOSE_OPEN),
    enum_select("xiaomi_back_wash", 7, 60, _CLOSE_OPEN),
    CARPET_AVOID,
    SWEEP_AVOID,
    MOP_AVOID,
    BACK_WASH_AREA,
    DRY_TIME,
    REMEMBER_MAP,
)


class _ExtraWireState(IntEnum):
    """Status codes the X20 spec adds after the shared sweep list."""

    WASHING = 9
    DRYING = 10
    DUST_COLLECTION = 11
    AIR_DRY_PAUSED = 12


X20: Final = XiaomiModel(
    model=MODEL_X20,
    property_overrides=compose_addresses(SWEEP_PROPERTIES),
    action_overrides=compose_addresses(SWEEP_ACTIONS),
    # Air-dry paused has no shell state, so it stays paused rather than drying.
    state_by_wire=compose_codes(
        SWEEP_STATES,
        {
            int(_ExtraWireState.WASHING): int(StoredState.WASHING),
            int(_ExtraWireState.DRYING): int(StoredState.DRYING),
            int(_ExtraWireState.DUST_COLLECTION): _LEGACY_AUTO_EMPTYING,
            int(_ExtraWireState.AIR_DRY_PAUSED): int(StoredState.PAUSED),
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

"""Mijia Robot Vacuum 4 record. The released spec is the S60 station slice with shorter lists."""

from __future__ import annotations

from typing import Final

from .model import (
    MODEL_MIJIA_ROBOT_VACUUM_4,
    XiaomiModel,
    control_with_options,
    regional_variant,
)
from .profile import (
    EXTENDED_STATION_CONTROLS,
    ExtendedStationWireState,
    ExtendedStationWireTask,
    StationWireState,
    StationWireTask,
    SummonWireState,
)
from .pv81gl import S60

_CLEAN_ONCE: Final = 1
_CLEAN_TWICE: Final = 2
_SILENT_CLEAN: Final = 0
_DEEP_CLEAN: Final = 1
_GENERAL: Final = 2
_CLEAN_TIMES: Final = control_with_options(
    EXTENDED_STATION_CONTROLS,
    "xiaomi_clean_times",
    (
        (_CLEAN_ONCE, "one_time"),
        (_CLEAN_TWICE, "two_time"),
    ),
)
_WORRY_FREE_MODE: Final = control_with_options(
    EXTENDED_STATION_CONTROLS,
    "xiaomi_worry_free_mode",
    (
        (_SILENT_CLEAN, "silent_clean"),
        (_DEEP_CLEAN, "deep_clean"),
        (_GENERAL, "general"),
    ),
)
_OMITTED_CONTROLS: Final = frozenset(
    {
        "xiaomi_carpet_deep_cleaning",
        "xiaomi_carpet_discriminate",
        "xiaomi_edge_sweep_frequency",
        "xiaomi_self_check_results",
        "xiaomi_stop_cut_hair",
        "xiaomi_sweep_carpet_first",
        "xiaomi_vibration_mop",
    }
)
_OMITTED_STATES: Final = (
    int(StationWireState.MULTI_TASK_STATION),
    int(StationWireState.STATION_WORKING),
    int(StationWireState.WASH_BREAK),
    int(ExtendedStationWireState.STATION_ASSISTING),
    int(ExtendedStationWireState.STATION_ASSISTED),
    int(SummonWireState.SELF_CHECK),
    int(SummonWireState.SUMMONING),
    int(SummonWireState.SWEEP_SUMMONING),
)
_OMITTED_TASKS: Final = (
    int(StationWireTask.EDGE),
    int(StationWireTask.CUSTOM),
    int(StationWireTask.POINT),
    int(ExtendedStationWireTask.LINKAGE),
    int(ExtendedStationWireTask.AI_HOSTING),
)

MIJIA_ROBOT_VACUUM_4: Final[XiaomiModel] = regional_variant(
    S60,
    MODEL_MIJIA_ROBOT_VACUUM_4,
    control_omitted=_OMITTED_CONTROLS,
    control_replaced={
        "xiaomi_clean_times": _CLEAN_TIMES,
        "xiaomi_worry_free_mode": _WORRY_FREE_MODE,
    },
    state_omitted=_OMITTED_STATES,
    task_omitted=_OMITTED_TASKS,
)

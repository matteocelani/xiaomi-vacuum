"""Mijia 6 Max record. Call clean is a sweep type, not the global action."""

from __future__ import annotations

from enum import IntEnum
from typing import Final

from .model import (
    MODEL_MIJIA_6_MAX,
    StoredTask,
    XiaomiModel,
    regional_variant,
    select_controls,
)
from .profile import EXTENDED_STATION_CONTROLS, S40_CLASS_CONTROLS
from .pv11gl import ROBOT_VACUUM_6_MAX

# The task enum has no summon code, so call-clean stays an automatic clean.
_ADDED_CONTROLS: Final = (
    *select_controls(
        EXTENDED_STATION_CONTROLS,
        (
            "xiaomi_dust_arrest_power",
            "xiaomi_start_station_self_clean",
            "xiaomi_stop_station_self_clean",
        ),
    ),
    *select_controls(S40_CLASS_CONTROLS, ("xiaomi_cut_hair_frequency",)),
)
_OMITTED_CONTROLS: Final = frozenset({"xiaomi_call_clean"})


class _CallCleanSweep(IntEnum):
    """Sweep-type code the Chinese spec adds for call clean."""

    CALL_CLEAN = 12


MIJIA_6_MAX: Final[XiaomiModel] = regional_variant(
    ROBOT_VACUUM_6_MAX,
    MODEL_MIJIA_6_MAX,
    control_additions=_ADDED_CONTROLS,
    control_omitted=_OMITTED_CONTROLS,
    task_overrides={int(_CallCleanSweep.CALL_CLEAN): int(StoredTask.AUTO_CLEANING)},
)

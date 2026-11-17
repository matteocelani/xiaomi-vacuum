"""Mijia Robot Vacuum 6 record, differing from Robot Vacuum 6 by start-eject."""

from __future__ import annotations

from typing import Final

from .model import (
    MODEL_MIJIA_ROBOT_VACUUM_6,
    XiaomiModel,
    regional_variant,
    select_controls,
)
from .profile import EXTENDED_STATION_CONTROLS
from .pv32gl import ROBOT_VACUUM_6

# Released version 2 adds this parameter-free action. Version 1 does not.
_START_EJECT: Final = select_controls(
    EXTENDED_STATION_CONTROLS, ("xiaomi_start_eject",)
)

MIJIA_ROBOT_VACUUM_6: Final[XiaomiModel] = regional_variant(
    ROBOT_VACUUM_6,
    MODEL_MIJIA_ROBOT_VACUUM_6,
    control_additions=_START_EJECT,
)

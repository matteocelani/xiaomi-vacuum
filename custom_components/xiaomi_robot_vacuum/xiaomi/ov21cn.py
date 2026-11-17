"""Mijia 5 Pro record, the Chinese ov21cn variant of Robot Vacuum 5 Pro."""

from __future__ import annotations

from typing import Final

from .controls import XiaomiControl, boolean_switch
from .model import (
    MODEL_MIJIA_5_PRO,
    XiaomiModel,
    regional_variant,
    select_controls,
)
from .ov21gl import ROBOT_VACUUM_5_PRO
from .profile import (
    EXTENDED_STATION_CONTROLS,
    HOST_TANK_WITH_NOT_INSTALLED,
    SELF_CHECK_RESULTS,
)

# Released names are Silent Clean and General, with Pet on the shared list.
_WORRY_FREE_MODE: Final[XiaomiControl] = select_controls(
    EXTENDED_STATION_CONTROLS, ("xiaomi_worry_free_mode",)
)[0]
# Already exposed on this model. The unnamed copies on other models stay disabled.
_PRECISE_DIAGNOSIS: Final = boolean_switch("xiaomi_precise_diagnosis", 20, 10)
MIJIA_5_PRO: Final[XiaomiModel] = regional_variant(
    ROBOT_VACUUM_5_PRO,
    MODEL_MIJIA_5_PRO,
    control_additions=(SELF_CHECK_RESULTS, _PRECISE_DIAGNOSIS),
    control_replaced={
        "xiaomi_host_tank": HOST_TANK_WITH_NOT_INSTALLED,
        "xiaomi_worry_free_mode": _WORRY_FREE_MODE,
    },
)

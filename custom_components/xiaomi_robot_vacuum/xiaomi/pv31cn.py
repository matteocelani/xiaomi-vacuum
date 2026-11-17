"""Mijia Robot Vacuum 5 record. Call-clean is absent and the host tank adds Not Installed."""

from __future__ import annotations

from typing import Final

from .model import MODEL_MIJIA_ROBOT_VACUUM_5, XiaomiModel, regional_variant
from .ov42gl import H50_PRO
from .profile import HOST_TANK_WITH_NOT_INSTALLED

_OMITTED_CONTROLS: Final = frozenset({"xiaomi_call_clean", "xiaomi_water_level_remind"})

MIJIA_ROBOT_VACUUM_5: Final[XiaomiModel] = regional_variant(
    H50_PRO,
    MODEL_MIJIA_ROBOT_VACUUM_5,
    control_omitted=_OMITTED_CONTROLS,
    control_replaced={"xiaomi_host_tank": HOST_TANK_WITH_NOT_INSTALLED},
)

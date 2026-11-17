"""Mijia M40 S record, the Chinese ov31cn variant of Robot Vacuum 5."""

from __future__ import annotations

from typing import Final

from .model import MODEL_MIJIA_M40_S, XiaomiModel, regional_variant
from .ov31gl import ROBOT_VACUUM_5
from .profile import SELF_CHECK_RESULTS

# Self-check items have no access, so only the readable result string is mapped.
MIJIA_M40_S: Final[XiaomiModel] = regional_variant(
    ROBOT_VACUUM_5,
    MODEL_MIJIA_M40_S,
    control_additions=(SELF_CHECK_RESULTS,),
)

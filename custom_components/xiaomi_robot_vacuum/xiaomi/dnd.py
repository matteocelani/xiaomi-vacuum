"""Set do-not-disturb through the sweep-family disturb action."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Final

from .exceptions import XiaomiControlException
from .model import (
    MODEL_E10,
    MODEL_E10C,
    MODEL_E12,
    MODEL_MIJIA_3C,
    MODEL_MIJIA_SWEEP_MOP_2,
    MODEL_MIJIA_SWEEP_MOP_3,
    MODEL_S12,
    MODEL_S20,
    MODEL_T12,
    MODEL_X20,
)

_SERVICE: Final = "xiaomi_set_dnd"
_SIID: Final = 12
_AIID: Final = 1
_INPUTS: Final = (1, 2, 3, 4, 5, 6)
_FIELD_PIIDS: Final = {
    "enable": 1,
    "start_hour": 2,
    "start_minute": 3,
    "end_hour": 4,
    "end_minute": 5,
    "timezone": 6,
}
_REQUIRED: Final = ("enable", "start_hour", "start_minute", "end_hour", "end_minute")
_ENABLE: Final = frozenset({0, 1})
_TIMEZONE: Final = 0

DND_MODELS: Final = frozenset(
    {
        MODEL_E10,
        MODEL_E10C,
        MODEL_E12,
        MODEL_MIJIA_3C,
        MODEL_MIJIA_SWEEP_MOP_2,
        MODEL_MIJIA_SWEEP_MOP_3,
        MODEL_S12,
        MODEL_S20,
        MODEL_T12,
        MODEL_X20,
    }
)


def set_dnd(device: object, fields: Mapping[str, object]) -> None:
    """Call set-notdisturb with one validated payload. Illegal values never leave."""
    model = _model_of(device)
    if model not in DND_MODELS:
        raise XiaomiControlException(_SERVICE)
    supplied = _validated_fields(fields)
    payload = [{"piid": piid, "value": supplied[piid]} for piid in _INPUTS]
    result = device._protocol.action(_SIID, _AIID, payload)
    if not isinstance(result, dict) or result.get("code") != 0:
        raise XiaomiControlException(_SERVICE)


def _model_of(device: object) -> str:
    codec = getattr(device, "_property_codec", None)
    model = getattr(codec, "model", None)
    if not isinstance(model, str) or not model:
        raise XiaomiControlException(_SERVICE)
    return model


def _validated_fields(fields: Mapping[str, object]) -> dict[int, int]:
    unknown = set(fields) - set(_FIELD_PIIDS)
    if unknown:
        raise XiaomiControlException(_SERVICE)
    for name in _REQUIRED:
        if name not in fields:
            raise XiaomiControlException(_SERVICE)
    supplied: dict[int, int] = {}
    for name, raw in fields.items():
        piid = _FIELD_PIIDS[name]
        value = _as_wire(name, raw)
        if not _allows(piid, value):
            raise XiaomiControlException(_SERVICE)
        supplied[piid] = value
    if 6 not in supplied:
        supplied[6] = _TIMEZONE
    return supplied


def _allows(piid: int, value: int) -> bool:
    if piid == 1:
        return value in _ENABLE
    if piid in (2, 4):
        return 0 <= value <= 23
    if piid in (3, 5):
        return 0 <= value <= 59
    return -99999 <= value <= 99999


def _as_wire(name: str, value: object) -> int:
    if name == "enable" and isinstance(value, bool):
        return 1 if value else 0
    if isinstance(value, bool) or not isinstance(value, int):
        raise XiaomiControlException(_SERVICE)
    return value

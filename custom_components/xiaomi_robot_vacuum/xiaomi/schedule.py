"""One add-schedule action for the sweep-family order service."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
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

_SERVICE: Final = "xiaomi_add_schedule"
_SIID: Final = 8
_AIID: Final = 4
_ORDER_PIIDS: Final = frozenset(range(2, 11))
_E10_MODELS: Final = frozenset({MODEL_E10, MODEL_E10C, MODEL_E12})
_E10_INPUTS: Final = (1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 14, 17, 19)
_OTHER_INPUTS: Final = (1, 2, 3, 4, 5, 6, 11, 12, 14, 16, 17, 19)
_FIELD_PIIDS: Final = {
    "enable": 2,
    "day": 3,
    "hour": 4,
    "minute": 5,
    "repeat": 6,
    "clean_way": 7,
    "suction": 8,
    "water": 9,
    "twice_clean": 10,
}
_REQUIRED_FIELDS: Final = ("enable", "day", "hour", "minute", "repeat")
# piid 10 is published on every model and is not an add-ii input on any of them.
_DEFAULTS: Final[dict[int, object]] = {
    1: 0,
    7: 0,
    8: 0,
    9: 0,
    11: 0,
    12: 0,
    14: 0,
    16: "",
    17: 0,
    19: 0,
}

SCHEDULE_MODELS: Final = frozenset(
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


@dataclass(frozen=True, slots=True)
class _Limits:
    """Value-list or range the spec publishes for one order piid."""

    values: frozenset[int] | None = None
    start: int | None = None
    end: int | None = None
    step: int = 1

    def allows(self, value: object) -> bool:
        """Return whether this wire value is inside the spec."""
        if isinstance(value, bool) or not isinstance(value, int):
            return False
        if self.values is not None:
            return value in self.values
        if self.start is None or self.end is None or self.step <= 0:
            return False
        if value < self.start or value > self.end:
            return False
        return (value - self.start) % self.step == 0


def _listed(*values: int) -> _Limits:
    return _Limits(values=frozenset(values))


def _span(start: int, end: int) -> _Limits:
    return _Limits(start=start, end=end, step=1)


_ENABLE: Final = _listed(0, 1)
_DAY: Final = _span(0, 255)
_HOUR: Final = _span(0, 23)
_MINUTE: Final = _span(0, 59)
_CLEAN_WAY: Final = _listed(0, 1, 2)
_SUCTION_FOUR: Final = _listed(0, 1, 2, 3)
_SUCTION_FIVE: Final = _listed(0, 1, 2, 3, 4)
_WATER_THREE: Final = _listed(0, 1, 2)
_WATER_FOUR: Final = _listed(0, 1, 2, 3)

_E10_LIMITS: Final = {
    2: _ENABLE,
    3: _DAY,
    4: _HOUR,
    5: _MINUTE,
    6: _ENABLE,
    7: _CLEAN_WAY,
    8: _SUCTION_FIVE,
    9: _WATER_FOUR,
    10: _ENABLE,
}
_OTHER_LIMITS: Final = {
    2: _ENABLE,
    3: _DAY,
    4: _HOUR,
    5: _MINUTE,
    6: _ENABLE,
    7: _CLEAN_WAY,
    8: _SUCTION_FOUR,
    9: _WATER_THREE,
    10: _ENABLE,
}


def schedule_property_name(model: str, siid: int, piid: int) -> str | None:
    """Return the schedule service name when this address is one of the 90 fields."""
    if model in SCHEDULE_MODELS and siid == _SIID and piid in _ORDER_PIIDS:
        return _SERVICE
    return None


def add_schedule(device: object, fields: Mapping[str, object]) -> None:
    """Call add-ii with one validated payload. Extra or illegal values never leave."""
    model = _model_of(device)
    if model not in SCHEDULE_MODELS:
        raise XiaomiControlException(_SERVICE)
    limits = _E10_LIMITS if model in _E10_MODELS else _OTHER_LIMITS
    accepted = _E10_INPUTS if model in _E10_MODELS else _OTHER_INPUTS
    supplied = _validated_fields(fields, limits, accepted)
    payload = [
        {"piid": piid, "value": _payload_value(piid, supplied, limits)}
        for piid in accepted
    ]
    result = device._protocol.action(_SIID, _AIID, payload)
    if not isinstance(result, dict) or result.get("code") != 0:
        raise XiaomiControlException(_SERVICE)


def _model_of(device: object) -> str:
    codec = getattr(device, "_property_codec", None)
    model = getattr(codec, "model", None)
    if not isinstance(model, str) or not model:
        raise XiaomiControlException(_SERVICE)
    return model


def _validated_fields(
    fields: Mapping[str, object],
    limits: Mapping[int, _Limits],
    accepted: tuple[int, ...],
) -> dict[int, int]:
    unknown = set(fields) - set(_FIELD_PIIDS)
    if unknown:
        raise XiaomiControlException(_SERVICE)
    for name in _REQUIRED_FIELDS:
        if name not in fields:
            raise XiaomiControlException(_SERVICE)
    supplied: dict[int, int] = {}
    for name, raw in fields.items():
        piid = _FIELD_PIIDS[name]
        value = _as_wire(raw)
        if not limits[piid].allows(value):
            raise XiaomiControlException(_SERVICE)
        if piid not in accepted:
            raise XiaomiControlException(_SERVICE)
        supplied[piid] = value
    return supplied


def _payload_value(
    piid: int, supplied: Mapping[int, int], limits: Mapping[int, _Limits]
) -> object:
    if piid in supplied:
        return supplied[piid]
    if piid in limits:
        default = _DEFAULTS[piid]
        if isinstance(default, int) and limits[piid].allows(default):
            return default
        raise XiaomiControlException(_SERVICE)
    if piid not in _DEFAULTS:
        raise XiaomiControlException(_SERVICE)
    return _DEFAULTS[piid]


def _as_wire(value: object) -> int:
    if isinstance(value, bool):
        return 1 if value else 0
    if isinstance(value, int):
        return value
    raise XiaomiControlException(_SERVICE)

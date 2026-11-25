"""Dreame-protocol robot that returns a generated floor plan."""

from __future__ import annotations

from typing import Final

from tests.virtual.floor_plan import encode_floor_plan

_STATE: Final = (2, 1)
_ERROR: Final = (2, 2)
_BATTERY: Final = (3, 1)
_CHARGING: Final = 6
_BATTERY_LEVEL: Final = 80
_STATUS: Final = (4, 1)
_CHARGING_STATUS: Final = (3, 2)
_CHARGE_LEVEL: Final = (28, 47)
_CHARGING_FLAG: Final = 1
_CHARGE_TARGET: Final = 100
_REQUEST_MAP: Final = (6, 1)
_MAP_DATA_PIID: Final = 1
_ROBOT_TIME_PIID: Final = 5
_STRING_ADDRESSES: Final = frozenset({(6, 1), (6, 2), (6, 3), (6, 4), (4, 57)})


class DreameMapRobot:
    """Answer Dreame miIO with a charging state and one I-frame map."""

    def __init__(self, model: str, mac: str = "00:00:00:00:00:fe") -> None:
        self.model = model
        self.mac = mac
        self.floor_plan = encode_floor_plan(current=True)
        self.actions: list[tuple[int, int]] = []
        self._published: dict[tuple[int, int], object] = {}

    def dispatch(self, method: object, params: object) -> object | None:
        """Return one Dreame miIO result."""
        if method == "miIO.info":
            return {
                "model": self.model,
                "fw_ver": "1.0_1",
                "mac": self.mac,
                "hw_ver": "Linux",
            }
        if method == "get_properties" and isinstance(params, list):
            return [self._read(item) for item in params if isinstance(item, dict)]
        if method == "set_properties" and isinstance(params, list):
            return [self._write(item) for item in params if isinstance(item, dict)]
        if method == "action" and isinstance(params, dict):
            return self._action(params)
        return None

    def _read(self, item: dict[str, object]) -> dict[str, object]:
        siid = item.get("siid")
        piid = item.get("piid")
        if not isinstance(siid, int) or not isinstance(piid, int):
            return {"code": -1}
        return {
            "did": item.get("did", ""),
            "siid": siid,
            "piid": piid,
            "code": 0,
            "value": self._value(siid, piid),
        }

    def _write(self, item: dict[str, object]) -> dict[str, object]:
        return {
            "did": item.get("did", ""),
            "siid": item.get("siid"),
            "piid": item.get("piid"),
            "code": 0,
        }

    def _action(self, params: dict[str, object]) -> dict[str, object]:
        siid = params.get("siid")
        aiid = params.get("aiid")
        if not isinstance(siid, int) or not isinstance(aiid, int):
            return {"code": -1}
        self.actions.append((siid, aiid))
        if (siid, aiid) != _REQUEST_MAP:
            return {"code": 0, "out": []}
        return {
            "code": 0,
            "out": [
                {"piid": _MAP_DATA_PIID, "value": self.floor_plan},
                {"piid": _ROBOT_TIME_PIID, "value": "1000"},
            ],
        }

    def publish(self, siid: int, piid: int, value: object) -> None:
        """Replace one property value, including a numeric zero."""
        self._published[(siid, piid)] = value

    def _value(self, siid: int, piid: int) -> object:
        address = (siid, piid)
        if address in self._published:
            return self._published[address]
        if address in (_STATE, _STATUS):
            return _CHARGING
        if address == _CHARGING_STATUS:
            return _CHARGING_FLAG
        if address == _CHARGE_LEVEL:
            return _CHARGE_TARGET
        if address == _ERROR:
            return 0
        if address == _BATTERY:
            return _BATTERY_LEVEL
        if address in _STRING_ADDRESSES:
            return ""
        return 0

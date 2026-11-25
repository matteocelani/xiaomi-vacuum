"""Room clean for Xiaomi models that publish a room-id action."""

from __future__ import annotations

from .exceptions import XiaomiControlException

_SERVICE = "room_sweep"


def supports_room_clean(device: object) -> bool:
    """Return whether this device can start a clean of named rooms."""
    return _address(device) is not None


def clean_rooms(device: object, segment_ids: object) -> None:
    """Start a room clean. The payload is the spec's room-id string."""
    address = _address(device)
    if address is None:
        raise XiaomiControlException(_SERVICE)
    siid, aiid, piid = address
    payload = [{"piid": piid, "value": _room_list(segment_ids)}]
    protocol = getattr(device, "_protocol", None)
    action = getattr(protocol, "action", None)
    if not callable(action):
        raise XiaomiControlException(_SERVICE)
    result = action(siid, aiid, payload)
    if not isinstance(result, dict) or result.get("code") != 0:
        raise XiaomiControlException(_SERVICE)


def _address(device: object) -> tuple[int, int, int] | None:
    codec = getattr(device, "_property_codec", None)
    address = getattr(codec, "room_sweep", None)
    if not isinstance(address, tuple) or len(address) != 3:
        return None
    siid, aiid, piid = address
    if not all(isinstance(item, int) for item in (siid, aiid, piid)):
        return None
    return siid, aiid, piid


def _room_list(segment_ids: object) -> str:
    if isinstance(segment_ids, int) and not isinstance(segment_ids, bool):
        raw_ids = (segment_ids,)
    elif isinstance(segment_ids, list):
        raw_ids = tuple(segment_ids)
    else:
        raise XiaomiControlException(_SERVICE)
    ids: list[int] = []
    for item in raw_ids:
        if isinstance(item, bool) or not isinstance(item, int) or item < 1:
            raise XiaomiControlException(_SERVICE)
        ids.append(item)
    if not ids:
        raise XiaomiControlException(_SERVICE)
    return ",".join(str(item) for item in ids)

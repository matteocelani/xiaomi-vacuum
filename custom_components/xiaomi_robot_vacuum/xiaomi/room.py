"""Room clean for Xiaomi models that publish a room-id action."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from .exceptions import XiaomiControlException

_SERVICE = "room_sweep"


@runtime_checkable
class _RoomCodec(Protocol):
    """A codec that names the room-sweep action."""

    room_sweep: tuple[int, int, int] | None


@runtime_checkable
class _SendsAction(Protocol):
    """The protocol object that can call one MIoT action."""

    def action(
        self,
        siid: int,
        aiid: int,
        parameters: object = None,
        retry_count: int = 2,
    ) -> object:
        """Send one action and return the device result."""


@runtime_checkable
class _RoomDevice(Protocol):
    """A device that can start a room clean."""

    _property_codec: _RoomCodec
    _protocol: _SendsAction


def supports_room_clean(device: object) -> bool:
    """Return whether this device can start a clean of named rooms."""
    return _address(device) is not None


def clean_rooms(device: object, segment_ids: object) -> None:
    """Start a room clean. The payload is the spec's room-id string."""
    address = _address(device)
    if address is None or not isinstance(device, _RoomDevice):
        raise XiaomiControlException(_SERVICE)
    protocol = device._protocol
    if not isinstance(protocol, _SendsAction):
        raise XiaomiControlException(_SERVICE)
    siid, aiid, piid = address
    payload = [{"piid": piid, "value": _room_list(segment_ids)}]
    result = protocol.action(siid, aiid, payload)
    if not isinstance(result, dict) or result.get("code") != 0:
        raise XiaomiControlException(_SERVICE)


def _address(device: object) -> tuple[int, int, int] | None:
    if not isinstance(device, _RoomDevice):
        return None
    codec = device._property_codec
    if not isinstance(codec, _RoomCodec):
        return None
    address = codec.room_sweep
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

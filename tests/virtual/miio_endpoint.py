"""Loopback miIO datagram server for one virtual robot."""

from __future__ import annotations

import hashlib
import json
import socket
import struct
import threading
from typing import Final, Protocol

from Crypto.Cipher import AES

_PORT: Final = 54321
_TOKEN: Final = "00" * 16
_HEADER: Final = 32


class MiioRobot(Protocol):
    """A robot that answers miIO methods."""

    def dispatch(self, method: object, params: object) -> object | None:
        """Return the result payload, or None when the method is unknown."""


def _plain(payload: bytes) -> bytes:
    if not payload:
        return payload
    pad_length = payload[-1]
    if (
        1 <= pad_length <= 16
        and payload[-pad_length:] == bytes([pad_length]) * pad_length
    ):
        payload = payload[:-pad_length]
    return payload.rstrip(b"\x00")


class MiioEndpoint:
    """Bind one loopback address and speak miIO for a spec robot."""

    def __init__(
        self,
        robot: MiioRobot,
        host: str = "127.0.0.1",
        token: str = _TOKEN,
    ) -> None:
        self.robot = robot
        self.host = host
        self.token = bytes.fromhex(token)
        self._stamp = 100
        self._device_id = 7
        self._socket: socket.socket | None = None
        self._thread: threading.Thread | None = None
        self._running = False
        key = hashlib.md5(self.token).digest()
        self._key = key
        self._iv = hashlib.md5(key + self.token).digest()

    def __enter__(self) -> MiioEndpoint:
        self.start()
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def start(self) -> None:
        """Bind the miIO port and answer in a background thread."""
        datagram = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        datagram.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        datagram.bind((self.host, _PORT))
        datagram.settimeout(0.2)
        self._socket = datagram
        self._running = True
        self._thread = threading.Thread(target=self._serve, name="spec-miio")
        self._thread.start()

    def close(self) -> None:
        """Stop the background thread and release the port."""
        self._running = False
        thread = self._thread
        if thread is not None:
            thread.join(timeout=2)
        datagram = self._socket
        if datagram is not None:
            datagram.close()
        self._socket = None

    def _serve(self) -> None:
        datagram = self._socket
        if datagram is None:
            return
        while self._running:
            try:
                packet, address = datagram.recvfrom(65535)
            except TimeoutError:
                continue
            except OSError:
                return
            reply = self._reply(packet)
            if reply is not None and self._running:
                datagram.sendto(reply, address)

    def _reply(self, packet: bytes) -> bytes | None:
        if len(packet) < 16:
            return None
        if struct.unpack(">H", packet[2:4])[0] == _HEADER or len(packet) == _HEADER:
            self._stamp += 1
            reply = bytearray(32)
            struct.pack_into(">HH", reply, 0, 0x2131, 32)
            struct.pack_into(">I", reply, 8, self._device_id)
            struct.pack_into(">I", reply, 12, self._stamp)
            reply[16:32] = b"\xff" * 16
            return bytes(reply)
        if len(packet) <= _HEADER:
            return None
        decrypted = self._decrypt(packet[_HEADER:])
        if decrypted is None:
            return self._reject()
        try:
            request = json.loads(_plain(decrypted))
        except (json.JSONDecodeError, UnicodeDecodeError, IndexError):
            return self._reject()
        if not isinstance(request, dict):
            return None
        result = self.robot.dispatch(request.get("method"), request.get("params"))
        if result is None:
            payload: dict[str, object] = {
                "id": request.get("id"),
                "error": {"code": -1},
            }
        else:
            payload = {"id": request.get("id"), "result": result}
        return self._encrypt(payload)

    def _reject(self) -> bytes:
        body = b"\x00" * 16
        header = struct.pack(">HH", 0x2131, _HEADER + len(body))
        header += b"\x00\x00\x00\x00"
        header += struct.pack(">II", self._device_id, self._stamp)
        return header + (b"\x00" * 16) + body

    def _decrypt(self, payload: bytes) -> bytes | None:
        if not payload or len(payload) % 16 != 0:
            return None
        return AES.new(self._key, AES.MODE_CBC, self._iv).decrypt(payload)

    def _encrypt(self, payload: object) -> bytes:
        raw = json.dumps(payload).encode() + b"\x00"
        pad_length = 16 - (len(raw) % 16)
        encrypted = AES.new(self._key, AES.MODE_CBC, self._iv).encrypt(
            raw + bytes([pad_length] * pad_length)
        )
        self._stamp += 1
        header = struct.pack(">HH", 0x2131, _HEADER + len(encrypted))
        header += b"\x00\x00\x00\x00"
        header += struct.pack(">II", self._device_id, self._stamp)
        checksum = hashlib.md5(header + self.token + encrypted).digest()
        return header + checksum + encrypted

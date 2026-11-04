"""Local miIO property transport without a network."""

from __future__ import annotations

import hashlib
import json
import logging
import struct

from Crypto.Cipher import AES
from custom_components.dreame_vacuum.xiaomi.exceptions import XiaomiTransportException
from custom_components.dreame_vacuum.xiaomi.transport import MiioPropertyTransport

_TOKEN = "00" * 16
_HOST = "127.0.0.1"
_PORT = 54321


class _ScriptedSocket:
    def __init__(
        self,
        scripts: list[bytes | BaseException],
        sources: list[tuple[str, int]] | None = None,
    ) -> None:
        self.scripts = scripts
        self.sources = sources
        self.sent: list[tuple[bytes, tuple[str, int]]] = []

    def settimeout(self, timeout: float | None) -> None:
        return None

    def sendto(self, data: bytes, address: tuple[str, int]) -> int:
        self.sent.append((data, address))
        return len(data)

    def recvfrom(self, bufsize: int) -> tuple[bytes, tuple[str, int]]:
        item = self.scripts.pop(0)
        if isinstance(item, BaseException):
            raise item
        if self.sources:
            return item, self.sources.pop(0)
        return item, (_HOST, _PORT)

    def close(self) -> None:
        return None


def _factory(
    scripts: list[bytes | BaseException],
    sources: list[tuple[str, int]] | None = None,
):
    sockets: list[_ScriptedSocket] = []

    def build() -> _ScriptedSocket:
        datagram = _ScriptedSocket(scripts, sources)
        sockets.append(datagram)
        return datagram

    return build, sockets


def _keys() -> tuple[bytes, bytes, bytes]:
    token = bytes.fromhex(_TOKEN)
    key = hashlib.md5(token).digest()
    iv = hashlib.md5(key + token).digest()
    return token, key, iv


def _handshake(device_id: int = 7, stamp: int = 100) -> bytes:
    packet = bytearray(32)
    struct.pack_into(">HH", packet, 0, 0x2131, 32)
    struct.pack_into(">I", packet, 8, device_id)
    struct.pack_into(">I", packet, 12, stamp)
    packet[16:32] = b"\xff" * 16
    return bytes(packet)


def _response(payload: object, stamp: int = 120) -> bytes:
    token, key, iv = _keys()
    raw = json.dumps(payload).encode()
    pad_length = 16 - (len(raw) % 16)
    encrypted = AES.new(key, AES.MODE_CBC, iv).encrypt(
        raw + bytes([pad_length] * pad_length)
    )
    header = struct.pack(">HH", 0x2131, 32 + len(encrypted)) + b"\x00\x00\x00\x00"
    header += struct.pack(">II", 7, stamp)
    checksum = hashlib.md5(header + token + encrypted).digest()
    return header + checksum + encrypted


def _cipher(plaintext: bytes, stamp: int = 120) -> bytes:
    token, key, iv = _keys()
    encrypted = AES.new(key, AES.MODE_CBC, iv).encrypt(plaintext)
    header = struct.pack(">HH", 0x2131, 32 + len(encrypted)) + b"\x00\x00\x00\x00"
    header += struct.pack(">II", 7, stamp)
    checksum = hashlib.md5(header + token + encrypted).digest()
    return header + checksum + encrypted


def _transport(
    scripts: list[bytes | BaseException],
    sources: list[tuple[str, int]] | None = None,
    clock=None,
) -> tuple[MiioPropertyTransport, list]:
    build, sockets = _factory(scripts, sources)
    return (
        MiioPropertyTransport(_HOST, _TOKEN, socket_factory=build, clock=clock),
        sockets,
    )


def _session(*after_probe: bytes | BaseException) -> list[bytes | BaseException]:
    return [
        _handshake(),
        _response({"id": 1, "result": {"model": "xiaomi.vacuum.d109gl"}}),
        *after_probe,
    ]


def test_invalid_token_is_rejected_without_echoing_it():
    for token in ("00", "zz" * 16, "0" * 31):
        try:
            MiioPropertyTransport(_HOST, token)
        except XiaomiTransportException as err:
            assert token not in str(err)
        else:
            raise AssertionError(token)


def test_probe_records_device_id_and_omits_secrets_from_the_failure_log(caplog):
    caplog.set_level(logging.DEBUG)
    transport, sockets = _transport(
        [_handshake(9, 40), _response({"id": 1, "result": {"model": "x"}})]
    )
    assert transport.probe() is True
    assert transport._device_id == 9
    assert transport._stamp == 120
    assert sockets[0].sent[0][0].startswith(bytes.fromhex("21310020"))
    assert sockets[0].sent[0][1] == (_HOST, _PORT)
    failed, _sockets = _transport([TimeoutError("timed out")])
    assert failed.probe() is False
    short, _more = _transport([b"\x00" * 8])
    assert short.probe() is False
    assert _TOKEN not in caplog.text
    assert _HOST not in caplog.text


def test_send_round_trips_a_property_request():
    transport, sockets = _transport(
        _session(_response({"id": 2, "result": [{"code": 0}]}))
    )
    result = transport.send("get_properties", [{"siid": 2, "piid": 1}], retry_count=0)
    assert result == [{"code": 0}]
    _token, key, iv = _keys()
    packet = sockets[2].sent[0][0]
    decrypted = AES.new(key, AES.MODE_CBC, iv).decrypt(packet[32:])
    decrypted = decrypted[: -decrypted[-1]]
    request = json.loads(decrypted)
    assert request["method"] == "get_properties"
    assert request["params"] == [{"siid": 2, "piid": 1}]
    assert transport._stamp == 120


def test_send_returns_none_when_the_robot_rejects_or_the_packet_is_unusable():
    rejected, _sockets = _transport(
        _session(_response({"id": 2, "error": {"code": -1}}))
    )
    assert rejected.send("set_properties", [], retry_count=0) is None
    plain, _plain_sockets = _transport(_session(_response({"id": 2, "value": 4})))
    assert plain.send("get_properties", retry_count=0) == {"id": 2, "value": 4}
    broken, _broken = _transport(_session(b"\x00" * 16))
    assert broken.send("get_properties", retry_count=0) is None
    bad_json, _bad_json = _transport(_session(_cipher(b"not-json" + bytes([8] * 8))))
    assert bad_json.send("get_properties", retry_count=0) is None
    odd_length, _odd = _transport(_session(b"\x00" * 40))
    assert odd_length.send("get_properties", retry_count=0) is None
    not_object, _not_object = _transport(_session(_response([])))
    assert not_object.send("get_properties", retry_count=0) is None
    bad_pad, _bad_pad = _transport(_session(_cipher(b"\x11" * 16)))
    assert bad_pad.send("get_properties", retry_count=0) is None
    mismatch, _mismatch = _transport(_session(_cipher(b"\x00" * 14 + bytes((1, 2)))))
    assert mismatch.send("get_properties", retry_count=0) is None
    timed_out, _timed = _transport(_session(TimeoutError("timed out")))
    assert timed_out.send("get_properties", retry_count=0) is None


def test_send_does_not_multiply_the_timeout_when_the_host_is_down():
    transport, sockets = _transport([TimeoutError("timed out")])
    assert transport.send("get_properties", retry_count=2) is None
    assert len(sockets) == 1
    assert transport.send("get_properties", retry_count=2) is None
    assert len(sockets) == 1


def test_open_uses_the_five_second_property_timeout():
    seen: list[float | None] = []

    class _RecordingSocket:
        def settimeout(self, timeout: float | None) -> None:
            seen.append(timeout)

    transport = MiioPropertyTransport(_HOST, _TOKEN, socket_factory=_RecordingSocket)
    transport._open()
    assert seen == [5.0]


def test_default_socket_factory_opens_without_sending(socket_enabled: None) -> None:
    transport = MiioPropertyTransport(_HOST, _TOKEN)
    datagram = transport._open()
    datagram.close()


def test_request_id_wraps_after_the_protocol_maximum():
    transport, _sockets = _transport([_response({"id": 1, "result": 1})])
    transport._discovered = True
    transport._request_id = 9999
    assert transport.send("get_properties", retry_count=0) == 1
    assert transport._request_id == 1


def _nul_response(payload: object) -> bytes:
    token, key, iv = _keys()
    raw = json.dumps(payload).encode() + b"\x00"
    pad_length = 16 - (len(raw) % 16)
    encrypted = AES.new(key, AES.MODE_CBC, iv).encrypt(
        raw + bytes([pad_length] * pad_length)
    )
    header = struct.pack(">HH", 0x2131, 32 + len(encrypted)) + b"\x00\x00\x00\x00"
    header += struct.pack(">II", 7, 120)
    checksum = hashlib.md5(header + token + encrypted).digest()
    return header + checksum + encrypted


def test_send_strips_the_trailing_nul_python_miio_appends():
    transport, _sockets = _transport(
        _session(_nul_response({"id": 2, "result": [{"code": 0, "value": 4}]}))
    )
    assert transport.send("get_properties", retry_count=0) == [{"code": 0, "value": 4}]


def test_send_rejects_a_response_whose_id_does_not_match():
    transport, _sockets = _transport(_session(_response({"id": 99, "result": 1})))
    assert transport.send("get_properties", retry_count=0) is None
    assert transport.local_auth_failed is False


def test_wrong_token_fails_the_probe_without_another_timeout():
    token = bytes.fromhex("ff" * 16)
    key = hashlib.md5(token).digest()
    iv = hashlib.md5(key + token).digest()
    raw = json.dumps({"id": 1, "result": {"model": "x"}}).encode()
    pad_length = 16 - (len(raw) % 16)
    encrypted = AES.new(key, AES.MODE_CBC, iv).encrypt(
        raw + bytes([pad_length] * pad_length)
    )
    header = struct.pack(">HH", 0x2131, 32 + len(encrypted)) + b"\x00\x00\x00\x00"
    header += struct.pack(">II", 7, 120)
    checksum = hashlib.md5(header + token + encrypted).digest()
    foreign = header + checksum + encrypted
    transport, sockets = _transport([_handshake(), foreign])
    assert transport.probe() is False
    assert transport.local_auth_failed is False
    assert transport.send("get_properties", retry_count=2) is None
    assert len(sockets) == 2


def test_spoofed_packets_do_not_latch_and_auth_failures_recover_after_backoff():
    spoofed, _sockets = _transport(
        [_handshake()],
        sources=[("192.0.2.8", _PORT)],
    )
    assert spoofed.probe() is False
    assert spoofed.local_auth_failed is False

    bad_checksum = bytearray(_response({"id": 1, "result": {"model": "x"}}))
    bad_checksum[16] ^= 0xFF
    mismatched, _more = _transport([_handshake(), bytes(bad_checksum)])
    assert mismatched.probe() is False
    assert mismatched.local_auth_failed is False

    now = {"at": 0.0}

    def clock() -> float:
        return now["at"]

    scripts: list[bytes | BaseException] = []
    for _attempt in range(3):
        scripts.extend([_handshake(), _cipher(b"not-json" + bytes([8] * 8))])
    scripts.extend(
        [
            _handshake(),
            _response({"id": 4, "result": {"model": "xiaomi.vacuum.d109gl"}}),
        ]
    )
    transport, sockets = _transport(scripts, clock=clock)
    for _attempt in range(3):
        assert transport.probe() is False
    assert transport.local_auth_failed is True
    assert transport.probe() is False
    assert len(sockets) == 6
    now["at"] = 31.0
    assert transport.probe() is True
    assert transport.local_auth_failed is False


def test_unsigned_handshake_is_accepted() -> None:
    hello = _handshake()
    assert hello[16:32] == b"\xff" * 16
    transport, _sockets = _transport(_session())
    assert transport.probe() is True
    assert transport.local_auth_failed is False


def test_handshake_rejects_the_wrong_magic() -> None:
    packet = bytearray(_handshake())
    packet[0] = 0
    transport, _sockets = _transport([bytes(packet)])
    assert transport.probe() is False
    assert transport.local_auth_failed is False


def test_three_checksum_failures_latch_auth() -> None:
    bad_checksum = bytearray(_response({"id": 1, "result": {"model": "x"}}))
    bad_checksum[16] ^= 0xFF
    scripts: list[bytes | BaseException] = []
    for _attempt in range(3):
        scripts.extend([_handshake(), bytes(bad_checksum)])
    transport, _sockets = _transport(scripts)
    for _attempt in range(3):
        assert transport.probe() is False
    assert transport.local_auth_failed is True

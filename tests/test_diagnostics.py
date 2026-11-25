"""Diagnostics redaction for values that must not leave the house."""

from __future__ import annotations

import importlib
import json
from pathlib import Path
import sys

_REDACTED = "**REDACTED**"
_SIGNED_URL = "https://maps.example.invalid/floor.tbz2?Expires=1&Signature=secret"


def _load_diagnostics():
    dreame_name = "custom_components.xiaomi_robot_vacuum.dreame"
    dreame = sys.modules.get(dreame_name)
    if dreame is not None and not hasattr(dreame, "VERSION"):
        init = (
            Path(__file__).resolve().parents[1]
            / "custom_components"
            / "xiaomi_robot_vacuum"
            / "dreame"
            / "__init__.py"
        )
        executed = compile(init.read_text(encoding="utf-8"), str(init), "exec")
        exec(executed, dreame.__dict__)
    package = "custom_components.xiaomi_robot_vacuum"
    module = sys.modules.get(package)
    if module is None or not hasattr(module, "async_setup_entry"):
        sys.modules.pop(package, None)
        importlib.import_module(package)
    return importlib.import_module("custom_components.xiaomi_robot_vacuum.diagnostics")


def test_matter_pairing_code_is_redacted() -> None:
    diagnostics = _load_diagnostics()
    payload = {
        "MATTER_QR_CODE": "MT:FAKE-PAIRING-CODE",
        "matter_qr_code": "MT:FAKE-PAIRING-CODE",
        "nested": {"matter_qr_code": "MT:ALSO-FAKE", "battery": 80},
    }

    sanitized = diagnostics.redact_diagnostics(payload)

    assert sanitized["MATTER_QR_CODE"] == _REDACTED
    assert sanitized["matter_qr_code"] == _REDACTED
    assert sanitized["nested"]["matter_qr_code"] == _REDACTED
    assert sanitized["nested"]["battery"] == 80
    assert "MT:" not in json.dumps(sanitized)


def test_secrets_geometry_and_signed_urls_are_redacted() -> None:
    diagnostics = _load_diagnostics()
    payload = {
        "entry": {
            "data": {
                "username": "person@example.invalid",
                "password": "secret-password",
                "token": "0" * 32,
                "auth_key": "auth-secret",
                "host": "192.0.2.10",
                "mac": "00:00:00:00:00:00",
                "did": "fake-did",
                "country": "de",
            }
        },
        "device": {"serial_number": "FAKESERIAL123", "model": "xiaomi.vacuum.example"},
        "note": _SIGNED_URL,
        "vacuum_position": {"x": 1200, "y": 3400},
        "rooms": [{"outline": [[1, 2], [3, 4]], "name": "Kitchen"}],
        "userId": "10001",
        "latitude": 52.52,
        "cookie": "serviceToken=fake",
    }

    sanitized = diagnostics.redact_diagnostics(payload)
    dumped = json.dumps(sanitized)

    assert sanitized["entry"]["data"]["country"] == "de"
    assert sanitized["device"]["model"] == "xiaomi.vacuum.example"
    for key in ("username", "password", "token", "auth_key", "host", "mac", "did"):
        assert sanitized["entry"]["data"][key] == _REDACTED
    assert sanitized["device"]["serial_number"] == _REDACTED
    assert sanitized["note"] == _REDACTED
    assert sanitized["vacuum_position"] == _REDACTED
    assert sanitized["rooms"] == _REDACTED
    assert sanitized["userId"] == _REDACTED
    assert sanitized["latitude"] == _REDACTED
    assert sanitized["cookie"] == _REDACTED
    for secret in (
        "secret-password",
        "auth-secret",
        "192.0.2.10",
        "FAKESERIAL123",
        "Signature=secret",
        "Kitchen",
        "serviceToken=fake",
        "1200",
    ):
        assert secret not in dumped


def test_property_enum_names_for_maps_and_stream_codes_are_redacted() -> None:
    """The property dump uses enum names, which are not the lowercase keys."""
    diagnostics = _load_diagnostics()
    secrets = {
        "MAP_DATA": "floor-secret-blob",
        "OLD_MAP_DATA": "old-floor",
        "OBJECT_NAME": "map-object-secret",
        "MAP_EXTEND_DATA": "extend-secret",
        "FRAME_INFO": "frame-secret",
        "CLEAN_LOG_FILE_NAME": "log-file-secret",
        "MAP_LIST": "map-list-secret",
        "STREAM_CODE": "stream-secret",
        "STREAM_SET_CODE": "stream-set-secret",
        "STREAM_VERIFY_CODE": "stream-verify-secret",
        "STREAM_RESET_CODE": "stream-reset-secret",
    }
    payload = {"properties": {**secrets, "battery": 80}}

    sanitized = diagnostics.redact_diagnostics(payload)
    dumped = json.dumps(sanitized)

    assert sanitized["properties"]["battery"] == 80
    for key in secrets:
        assert sanitized["properties"][key] == _REDACTED
    for secret in secrets.values():
        assert secret not in dumped


def test_diagnostics_do_not_build_a_map_image() -> None:
    source = Path("custom_components/xiaomi_robot_vacuum/diagnostics.py").read_text(
        encoding="utf-8"
    )
    assert "async_redact_data" in source
    assert "DreameVacuumMapRenderer" not in source
    assert "_map_payloads" not in source

"""Signed cloud file URLs stay out of log lines."""

from __future__ import annotations

from pathlib import Path
import re

from custom_components.xiaomi_robot_vacuum.dreame.protocol import cloud_object_key

_DREAME = Path("custom_components/xiaomi_robot_vacuum/dreame")
_RAW_URL_ARGUMENT = re.compile(r"_LOGGER\.\w+\([^)\n]*\b(?:url|map_url)\b")


def test_cloud_object_key_drops_signed_query() -> None:
    """The object key keeps the path and drops the signed query and userinfo."""
    url = (
        "https://user:token@example.invalid/maps/floor/object.tbz2"
        "?Expires=1&Signature=secret&OSSAccessKeyId=key"
    )
    key = cloud_object_key(url)
    assert key == "maps/floor/object.tbz2"
    assert "Signature" not in key
    assert "secret" not in key
    assert "token" not in key


def test_cloud_object_key_empty_is_stable() -> None:
    """A URL with no path still produces a label that is safe to log."""
    assert cloud_object_key("") == "map-object"
    assert cloud_object_key("https://example.invalid") == "map-object"
    assert cloud_object_key("https://example.invalid/?Signature=secret") == "map-object"


def test_map_and_protocol_logger_lines_omit_file_urls() -> None:
    """Logger calls do not take the signed URL or the raw file-url response."""
    for name in ("map.py", "protocol.py"):
        text = (_DREAME / name).read_text(encoding="utf-8")
        for lineno, line in enumerate(text.splitlines(), start=1):
            assert _RAW_URL_ARGUMENT.search(line) is None, f"{name}:{lineno}:{line}"
        assert "Get file url result: %s = %s" not in text
        assert "Get interim file url result: %s = %s" not in text
        assert "Unable to get file at %s" not in text
        assert "Recovery map file url:" not in text


def test_logger_lines_omit_response_bodies_and_map_payloads() -> None:
    """Auth responses and decoded map bytes are not log arguments."""
    protocol = (_DREAME / "protocol.py").read_text(encoding="utf-8")
    for lineno, line in enumerate(protocol.splitlines(), start=1):
        if "_LOGGER." not in line:
            continue
        assert "content.decode" not in line, f"protocol.py:{lineno}:{line}"
        assert "response.text" not in line, f"protocol.py:{lineno}:{line}"
        assert "content[:200]" not in line, f"protocol.py:{lineno}:{line}"
    map_source = (_DREAME / "map.py").read_text(encoding="utf-8")
    for lineno, line in enumerate(map_source.splitlines(), start=1):
        if "_LOGGER." not in line:
            continue
        assert "raw_data" not in line, f"map.py:{lineno}:{line}"
        if "data_json" in line:
            assert "len(data_json)" in line, f"map.py:{lineno}:{line}"
    assert "session.get(url)" not in protocol
    assert "session.get(url, timeout=10)" in protocol

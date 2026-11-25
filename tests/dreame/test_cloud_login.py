"""Dreame cloud login keeps a successful token when expiry is not an int."""

from __future__ import annotations

import json

from custom_components.xiaomi_robot_vacuum.dreame import protocol
import pytest

_NOW = 1_700_000_000
_PASSWORD = "secret-password"
_USERNAME = "person@example.invalid"


def _dreame(
    monkeypatch: pytest.MonkeyPatch, country: str
) -> protocol.DreameVacuumDreameHomeCloudProtocol:
    monkeypatch.setattr(protocol.time, "time", lambda: _NOW)
    return protocol.DreameVacuumDreameHomeCloudProtocol(
        _USERNAME, _PASSWORD, country=country
    )


def _reply(**fields: object) -> bytes:
    return json.dumps(fields).encode("utf-8")


def test_login_accepts_a_string_expiry_and_uses_the_region(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """expires_in arrives as a string on some replies, and the host follows the country."""
    seen: dict[str, str] = {}

    def http(
        method: str, url: str, headers: object, data: object, timeout: object
    ) -> tuple[int, bytes]:
        del method, headers, data, timeout
        seen["url"] = url
        return 200, _reply(
            access_token="access-fake",
            refresh_token="refresh-fake",
            expires_in="3600",
            uid="1",
            region="de",
            country="de",
        )

    cloud = _dreame(monkeypatch, "de")
    cloud._http = http

    assert cloud.login() is True
    assert seen["url"] == "https://de.iot.dreame.tech:13267/dreame-auth/oauth/token"
    assert cloud._key == "access-fake"
    assert cloud._secondary_key == "refresh-fake"
    assert cloud._key_expire == _NOW + 3600
    assert cloud._region == "de"


def test_login_succeeds_when_expiry_is_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    """A 200 without expires_in is still a login. The next call can refresh."""

    def http(
        method: str, url: str, headers: object, data: object, timeout: object
    ) -> tuple[int, bytes]:
        del method, url, headers, data, timeout
        return 200, _reply(
            access_token="access-fake", refresh_token="refresh-fake", uid="1"
        )

    cloud = _dreame(monkeypatch, "cn")
    cloud._http = http

    assert cloud.login() is True
    assert cloud._key == "access-fake"
    assert cloud._secondary_key == "refresh-fake"
    assert cloud._key_expire is None


def test_rejected_refresh_token_falls_back_to_the_password(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A dead refresh token is cleared once, then the password grant runs."""
    bodies: list[str] = []

    def http(
        method: str, url: str, headers: object, data: object, timeout: object
    ) -> tuple[int, bytes]:
        del method, url, headers, timeout
        bodies.append(data.decode("utf-8") if isinstance(data, bytes) else str(data))
        if len(bodies) == 1:
            return 401, _reply(error_description="refresh token expired")
        return 200, _reply(
            access_token="access-fake",
            refresh_token="refresh-new",
            expires_in=3600,
        )

    cloud = _dreame(monkeypatch, "us")
    cloud._secondary_key = "old-refresh"
    cloud._http = http

    assert cloud.login() is True
    assert cloud._key == "access-fake"
    assert cloud._secondary_key == "refresh-new"
    assert "refresh_token=old-refresh" in bodies[0]
    assert "grant_type=password" in bodies[1]
    assert "grant_type=refresh_token" not in bodies[1]


def test_mi_home_region_prefix() -> None:
    """Mainland China has no host prefix. Every other region does."""
    china = protocol.DreameVacuumMiHomeCloudProtocol(_USERNAME, _PASSWORD, "cn")
    germany = protocol.DreameVacuumMiHomeCloudProtocol(_USERNAME, _PASSWORD, "de")

    assert china.get_api_url() == "https://api.io.mi.com/app"
    assert germany.get_api_url() == "https://de.api.io.mi.com/app"

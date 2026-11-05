"""Mi Home 2FA follows only Xiaomi's optional phone-confirmation skip."""

from __future__ import annotations

import logging

from custom_components.dreame_vacuum.dreame.protocol import (
    DreameVacuumMiHomeCloudProtocol,
)
import pytest

_PHONE = "https://account.xiaomi.com/fe/service/verifyPhone"


class _Response:
    def __init__(self, url: str, status_code: int = 200) -> None:
        self.url = url
        self.status_code = status_code


class _Session:
    def __init__(
        self, result: object | None = None, error: Exception | None = None
    ) -> None:
        self.urls: list[str] = []
        self._result = result
        self._error = error

    def get(
        self, url: str, headers: dict[str, str], allow_redirects: bool, timeout: int
    ) -> object:
        del headers, allow_redirects, timeout
        self.urls.append(url)
        if self._error is not None:
            raise self._error
        return self._result


def _protocol() -> DreameVacuumMiHomeCloudProtocol:
    return object.__new__(DreameVacuumMiHomeCloudProtocol)


def test_optional_phone_confirmation_follows_a_xiaomi_skip_url() -> None:
    followed = _Response("https://account.xiaomi.com/pass/serviceLogin")
    session = _Session(result=followed)
    response = _Response(
        f"{_PHONE}?skipUrl=https%3A%2F%2Faccount.xiaomi.com%2Fpass%2FserviceLogin"
    )

    result = _protocol()._follow_phone_confirmation(response, session, {})

    assert result is followed
    assert session.urls == ["https://account.xiaomi.com/pass/serviceLogin"]


def test_phone_confirmation_ignores_an_offsite_skip_url(
    caplog: pytest.LogCaptureFixture,
) -> None:
    session = _Session(result=_Response("https://evil.example/stolen"))
    response = _Response(f"{_PHONE}?skipUrl=https%3A%2F%2Fevil.example%2Fstolen")

    with caplog.at_level(logging.WARNING):
        result = _protocol()._follow_phone_confirmation(response, session, {})

    assert result is response
    assert session.urls == []
    assert any("unexpected" in record.getMessage() for record in caplog.records)


def test_phone_confirmation_failure_does_not_log_the_redirect(
    caplog: pytest.LogCaptureFixture,
) -> None:
    secret = "skip-token-not-for-logs"
    session = _Session(error=TimeoutError(f"timed out fetching {secret}"))
    response = _Response(
        f"{_PHONE}?skipUrl=https%3A%2F%2Faccount.xiaomi.com%2Fpass%2Flogin%3F{secret}"
    )

    with caplog.at_level(logging.WARNING):
        result = _protocol()._follow_phone_confirmation(response, session, {})

    assert result is response
    assert secret not in caplog.text
    assert any("TimeoutError" in record.getMessage() for record in caplog.records)

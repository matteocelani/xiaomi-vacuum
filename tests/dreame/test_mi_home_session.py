"""Xiaomi Home retries one command after the service token expires."""

from __future__ import annotations

import base64
from types import SimpleNamespace

from custom_components.xiaomi_robot_vacuum.dreame import protocol

_NONCE = base64.b64encode(b"0123456789abcdef").decode()


def _cloud() -> protocol.DreameVacuumMiHomeCloudProtocol:
    cloud = protocol.DreameVacuumMiHomeCloudProtocol(
        "person@example.invalid",
        "secret-password",
        "de",
    )
    cloud._ssecurity = _NONCE
    cloud._service_token = "service-token"
    cloud._userId = "10001"
    cloud.generate_enc_params = lambda *_args: {"_nonce": _NONCE}
    cloud.signed_nonce = lambda _nonce: _NONCE
    cloud.decrypt_rc4 = lambda _password, _payload: b'{"code":0,"result":{"ok":1}}'
    return cloud


def test_an_expired_mi_home_session_retries_the_command() -> None:
    """A 401 logs in once and sends the same command again."""
    cloud = _cloud()
    posts: list[int] = []

    class _Session:
        def post(
            self,
            url: str,
            headers: object,
            cookies: object,
            data: object,
            timeout: object,
        ) -> SimpleNamespace:
            del url, headers, cookies, data, timeout
            posts.append(1)
            return SimpleNamespace(
                status_code=401 if len(posts) == 1 else 200, text="x"
            )

        def close(self) -> None:
            return None

    cloud._session_obj = _Session()
    logins: list[bool] = []
    cloud.login = lambda: logins.append(True) or True

    result = cloud.request("https://de.api.io.mi.com/app/v2/home/rpc", {"data": "{}"})

    assert logins == [True]
    assert len(posts) == 2
    assert result == {"code": 0, "result": {"ok": 1}}

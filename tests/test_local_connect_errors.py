"""Local setup reports a bad token separately from an offline robot."""

from __future__ import annotations

import importlib
from pathlib import Path
import sys

import pytest
from tests.virtual.fleet_catalog import robot_profiles
from tests.virtual.miio_endpoint import MiioEndpoint
from tests.virtual.spec_robot import SpecRobot

from homeassistant.const import CONF_HOST, CONF_TOKEN
from homeassistant.core import HomeAssistant

pytestmark = [
    pytest.mark.ha,
    pytest.mark.enable_socket,
    pytest.mark.allow_hosts(["127.0.0.73", "127.0.0.74"]),
]

_GOOD = "00" * 16
_BAD = "ff" * 16
_HOST = "127.0.0.73"
_OFFLINE = "127.0.0.74"
_MAC = "00:00:00:00:00:73"
_MODEL = "xiaomi.vacuum.b108gl"


def _load_flow():
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
        module = importlib.import_module(package)
    return importlib.import_module(f"{package}.config_flow")


def _handler(hass: HomeAssistant, flow):
    handler = flow.DreameVacuumFlowHandler()
    handler.hass = hass
    handler.account_type = "local"
    handler.prefer_cloud = True
    return handler


def _robot() -> SpecRobot:
    profile = next(item.document() for item in robot_profiles() if item.model == _MODEL)
    return SpecRobot(_MODEL, profile, mac=_MAC)


async def test_a_checksum_failure_is_a_wrong_token(
    hass: HomeAssistant, socket_enabled: None
) -> None:
    """A robot that answers with another token is not reported as offline."""
    del socket_enabled
    flow = _load_flow()
    handler = _handler(hass, flow)
    with MiioEndpoint(_robot(), host=_HOST):
        result = await handler.async_step_local({CONF_HOST: _HOST, CONF_TOKEN: _BAD})
    assert result["type"] == "form"
    assert result["step_id"] == "local"
    assert result["errors"]["base"] == "wrong_token"


async def test_a_short_token_is_a_wrong_token(hass: HomeAssistant) -> None:
    """A token that is not 32 hex characters never opens a socket."""
    flow = _load_flow()
    handler = _handler(hass, flow)
    result = await handler.async_step_local({CONF_HOST: _HOST, CONF_TOKEN: "abcd"})
    assert result["type"] == "form"
    assert result["errors"]["base"] == "wrong_token"


async def test_an_offline_robot_cannot_connect(hass: HomeAssistant) -> None:
    """A valid token with nobody listening is a connection failure."""
    flow = _load_flow()
    handler = _handler(hass, flow)
    result = await handler.async_step_local({CONF_HOST: _OFFLINE, CONF_TOKEN: _GOOD})
    assert result["type"] == "form"
    assert result["errors"]["base"] == "cannot_connect"

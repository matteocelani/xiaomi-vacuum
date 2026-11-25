"""Reauthentication on the oldest Home Assistant this integration supports."""

from __future__ import annotations

import importlib
from pathlib import Path
import sys

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_TOKEN,
    CONF_USERNAME,
)
from homeassistant.core import HomeAssistant

pytestmark = pytest.mark.ha

_OLD_TOKEN = "11" * 16
_NEW_TOKEN = "22" * 16
_MAC = "00:00:00:00:00:11"


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
    return module, importlib.import_module(f"{package}.config_flow")


class _Cloud:
    auth_key = "auth-key"


class _Protocol:
    def __init__(self, *_args: object, **_kwargs: object) -> None:
        self.cloud = _Cloud()

    def connect(self, *_args: object) -> dict[str, str]:
        return {"mac": _MAC, "model": "xiaomi.vacuum.b108gl"}

    def disconnect(self) -> None:
        return None


def _handler(hass: HomeAssistant, flow, entry: MockConfigEntry):
    handler = flow.DreameVacuumFlowHandler()
    handler.hass = hass
    handler.context = {"source": "reauth", "entry_id": entry.entry_id}
    handler.reauth = True
    handler.host = "127.0.0.2"
    handler.token = _NEW_TOKEN
    handler.username = "lab"
    handler.password = "lab-secret"
    handler.country = "eu"
    handler.account_type = "mi"
    handler.prefer_cloud = True
    return handler


def _entry(package, hass: HomeAssistant) -> MockConfigEntry:
    entry = MockConfigEntry(
        domain=package.DOMAIN,
        unique_id=_MAC,
        title="Vac",
        data={
            CONF_NAME: "Vac",
            CONF_HOST: "127.0.0.1",
            CONF_TOKEN: _OLD_TOKEN,
            CONF_USERNAME: "old",
            CONF_PASSWORD: "old-secret",
        },
    )
    entry.add_to_hass(hass)
    return entry


async def test_reauth_saves_the_token_on_a_2024_3_helper(
    hass: HomeAssistant, monkeypatch: pytest.MonkeyPatch
) -> None:
    """2024.3 reloads from data=, and rejects the later data_updates argument."""
    package, flow = _load_flow()
    entry = _entry(package, hass)

    def legacy(self, stored, *, data, **kwargs):
        hass.config_entries.async_update_entry(stored, data=data)
        return self.async_abort(reason=kwargs.get("reason", "reauth_successful"))

    monkeypatch.setattr(flow, "DreameVacuumProtocol", _Protocol)
    monkeypatch.setattr(
        flow.DreameVacuumFlowHandler, "async_update_reload_and_abort", legacy
    )
    result = await _handler(hass, flow, entry).async_step_connect()

    assert result["type"] == "abort"
    assert result["reason"] == "reauth_successful"
    assert entry.data[CONF_TOKEN] == _NEW_TOKEN
    assert entry.data[CONF_HOST] == "127.0.0.2"
    assert entry.data[CONF_USERNAME] == "lab"
    assert entry.data[CONF_PASSWORD] == "lab-secret"
    assert entry.data[CONF_NAME] == "Vac"


async def test_reauth_saves_the_token_on_current_home_assistant(
    hass: HomeAssistant, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Current core merges data_updates and reloads the same entry."""
    package, flow = _load_flow()
    entry = _entry(package, hass)
    scheduled: list[str] = []
    monkeypatch.setattr(flow, "DreameVacuumProtocol", _Protocol)
    monkeypatch.setattr(
        hass.config_entries,
        "async_schedule_reload",
        lambda entry_id: scheduled.append(entry_id),
    )
    result = await _handler(hass, flow, entry).async_step_connect()

    assert result["type"] == "abort"
    assert result["reason"] == "reauth_successful"
    assert entry.data[CONF_TOKEN] == _NEW_TOKEN
    assert entry.data["auth_key"] == "auth-key"
    assert scheduled == [entry.entry_id]


async def test_reauth_saves_the_token_on_home_assistant_2024_2(
    hass: HomeAssistant, monkeypatch: pytest.MonkeyPatch
) -> None:
    """2024.2 has neither the reauth helper nor a scheduled reload."""
    package, flow = _load_flow()
    entry = _entry(package, hass)
    scheduled: list[str] = []

    monkeypatch.setattr(flow, "DreameVacuumProtocol", _Protocol)
    monkeypatch.setattr(
        flow.DreameVacuumFlowHandler, "async_update_reload_and_abort", None
    )
    monkeypatch.setattr(flow.DreameVacuumFlowHandler, "_get_reauth_entry", None)
    monkeypatch.setattr(
        hass.config_entries,
        "async_schedule_reload",
        None,
    )

    async def reload(entry_id: str) -> None:
        scheduled.append(entry_id)

    monkeypatch.setattr(hass.config_entries, "async_reload", reload)
    result = await _handler(hass, flow, entry).async_step_connect()
    await hass.async_block_till_done()

    assert result["type"] == "abort"
    assert result["reason"] == "reauth_successful"
    assert entry.data[CONF_TOKEN] == _NEW_TOKEN
    assert scheduled == [entry.entry_id]

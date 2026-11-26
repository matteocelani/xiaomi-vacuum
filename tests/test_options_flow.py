"""Options flow for a local entry, which has no cloud username."""

from __future__ import annotations

import importlib
from pathlib import Path
import sys

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.const import CONF_HOST, CONF_MAC, CONF_NAME, CONF_TOKEN
from homeassistant.core import HomeAssistant

pytestmark = pytest.mark.ha

_TOKEN = "00" * 16
_MAC = "00:00:00:00:00:11"


def _models() -> tuple[str, ...]:
    from custom_components.xiaomi_robot_vacuum.dreame.catalog import (
        load_model_catalog,
    )
    from custom_components.xiaomi_robot_vacuum.dreame.const import DEVICE_INFO
    from custom_components.xiaomi_robot_vacuum.xiaomi.mapping import _FAMILIES

    dreame = sorted(
        model
        for model in load_model_catalog(DEVICE_INFO)
        if model.startswith("dreame.")
    )
    return (*_FAMILIES, dreame[0])


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
    flow = importlib.import_module(f"{package}.config_flow")
    return module, flow


@pytest.mark.parametrize("model", _models())
async def test_local_options_flow_opens_without_a_username(
    hass: HomeAssistant, model: str
) -> None:
    """A local entry has no username. The options form still opens."""
    package, flow = _load_flow()
    entry = MockConfigEntry(
        domain=package.DOMAIN,
        title=model,
        data={
            CONF_NAME: model,
            CONF_HOST: "127.0.0.1",
            CONF_TOKEN: _TOKEN,
            CONF_MAC: _MAC,
            "model": model,
            "account_type": "mi",
        },
        options={"notify": False, "prefer_cloud": False},
    )
    entry.add_to_hass(hass)
    handler = flow.DreameVacuumOptionsFlowHandler(entry)
    handler.hass = hass
    result = await handler.async_step_init(None)
    assert result["type"] == "form"
    assert result["step_id"] == "init"

    saved = await handler.async_step_init({"notify": ["cleanup_completed"]})
    assert saved["type"] == "create_entry"
    assert saved["data"]["notify"] == ["cleanup_completed"]
    assert saved["data"]["prefer_cloud"] is False


async def test_cloud_options_still_include_map_settings(hass: HomeAssistant) -> None:
    """A stored username still opens the map and color settings."""
    package, flow = _load_flow()
    entry = MockConfigEntry(
        domain=package.DOMAIN,
        data={
            CONF_NAME: "Cloud",
            CONF_HOST: "127.0.0.1",
            CONF_TOKEN: _TOKEN,
            CONF_MAC: _MAC,
            "username": "person@example.com",
            "account_type": "mi",
        },
        options={
            "notify": False,
            "prefer_cloud": True,
            "color_scheme": "dreame_light",
            "icon_set": "dreame",
        },
    )
    entry.add_to_hass(hass)
    handler = flow.DreameVacuumOptionsFlowHandler(entry)
    handler.hass = hass
    result = await handler.async_step_init(None)
    assert result["type"] == "form"
    markers = {key.schema for key in result["data_schema"].schema}
    assert "color_scheme" in markers
    assert "icon_set" in markers
    assert "prefer_cloud" in markers


async def test_cloud_options_open_when_color_scheme_was_never_stored(
    hass: HomeAssistant,
) -> None:
    """A username without a stored color scheme still opens the form."""
    package, flow = _load_flow()
    entry = MockConfigEntry(
        domain=package.DOMAIN,
        data={
            CONF_NAME: "Cloud",
            CONF_HOST: "127.0.0.1",
            CONF_TOKEN: _TOKEN,
            CONF_MAC: _MAC,
            "username": "person@example.com",
            "account_type": "mi",
        },
        options={"notify": False, "prefer_cloud": True},
    )
    entry.add_to_hass(hass)
    handler = flow.DreameVacuumOptionsFlowHandler(entry)
    handler.hass = hass
    result = await handler.async_step_init(None)
    assert result["type"] == "form"
    markers = {key.schema for key in result["data_schema"].schema}
    assert "color_scheme" in markers

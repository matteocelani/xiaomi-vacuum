"""Config-entry migration that drops the removed card license key."""

from __future__ import annotations

import importlib
from pathlib import Path
import sys

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.const import CONF_HOST, CONF_NAME, CONF_TOKEN
from homeassistant.core import HomeAssistant

pytestmark = pytest.mark.ha

_TOKEN = "0" * 32
_LICENSE = "0" * 32


def _load_package():
    dreame_name = "custom_components.dreame_vacuum.dreame"
    dreame = sys.modules.get(dreame_name)
    if dreame is not None and not hasattr(dreame, "VERSION"):
        init = (
            Path(__file__).resolve().parents[1]
            / "custom_components"
            / "dreame_vacuum"
            / "dreame"
            / "__init__.py"
        )
        executed = compile(init.read_text(encoding="utf-8"), str(init), "exec")
        exec(executed, dreame.__dict__)
    package = "custom_components.dreame_vacuum"
    module = sys.modules.get(package)
    if module is None or not hasattr(module, "async_migrate_entry"):
        sys.modules.pop(package, None)
        module = importlib.import_module(package)
    return module


async def test_migrate_entry_drops_card_license_and_keeps_identity(
    hass: HomeAssistant,
) -> None:
    """Version 1 entries lose the license key and keep the rest of the entry."""
    package = _load_package()
    entry = MockConfigEntry(
        domain=package.DOMAIN,
        version=1,
        unique_id="00:00:00:00:00:00",
        title="Vac",
        data={
            CONF_NAME: "Vac",
            CONF_HOST: "127.0.0.1",
            CONF_TOKEN: _TOKEN,
            package.CONF_DVC_KEY: _LICENSE,
        },
        options={
            "notify": False,
            "version": "v2.1.1",
            package.CONF_DVC_KEY: _LICENSE,
        },
    )
    entry.add_to_hass(hass)

    assert await package.async_migrate_entry(hass, entry)

    assert entry.version == 2
    assert entry.unique_id == "00:00:00:00:00:00"
    assert package.CONF_DVC_KEY not in entry.data
    assert package.CONF_DVC_KEY not in entry.options
    assert entry.data[CONF_HOST] == "127.0.0.1"
    assert entry.data[CONF_TOKEN] == _TOKEN
    assert entry.data[CONF_NAME] == "Vac"
    assert entry.options["notify"] is False
    assert entry.options["version"] == "v2.1.1"


async def test_migrate_entry_is_idempotent_when_already_version_2(
    hass: HomeAssistant,
) -> None:
    """A version 2 entry is left unchanged."""
    package = _load_package()
    options = {"notify": True, "version": "v2.1.2"}
    data = {CONF_NAME: "Vac", CONF_HOST: "127.0.0.1", CONF_TOKEN: _TOKEN}
    entry = MockConfigEntry(
        domain=package.DOMAIN,
        version=2,
        unique_id="00:00:00:00:00:00",
        data=dict(data),
        options=dict(options),
    )
    entry.add_to_hass(hass)

    assert await package.async_migrate_entry(hass, entry)

    assert entry.version == 2
    assert dict(entry.data) == data
    assert dict(entry.options) == options


async def test_migrate_entry_bumps_version_when_license_is_already_absent(
    hass: HomeAssistant,
) -> None:
    """Version 1 entries that never stored the key still move to version 2."""
    package = _load_package()
    entry = MockConfigEntry(
        domain=package.DOMAIN,
        version=1,
        data={CONF_NAME: "Vac", CONF_HOST: "127.0.0.1", CONF_TOKEN: _TOKEN},
        options={"notify": False},
    )
    entry.add_to_hass(hass)

    assert await package.async_migrate_entry(hass, entry)

    assert entry.version == 2
    assert dict(entry.options) == {"notify": False}
    assert package.CONF_DVC_KEY not in entry.data

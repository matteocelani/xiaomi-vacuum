"""Device work must not touch Home Assistant off the loop, or block it."""

from __future__ import annotations

import asyncio
import importlib
from pathlib import Path
import sys
import threading

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.components import persistent_notification
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_TOKEN
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

pytestmark = pytest.mark.ha

_TOKEN = "00" * 16
_MAC = "00:00:00:00:00:60"


def _load_package():
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


def _coordinator(hass: HomeAssistant):
    _load_package()
    from custom_components.xiaomi_robot_vacuum.const import (
        CONF_MAC,
        CONF_NOTIFY,
        CONF_VERSION,
        DOMAIN,
    )
    from custom_components.xiaomi_robot_vacuum.coordinator import (
        DreameVacuumDataUpdateCoordinator,
    )
    from custom_components.xiaomi_robot_vacuum.dreame import VERSION

    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id=_MAC,
        title="Vac",
        data={
            CONF_NAME: "Vac",
            CONF_HOST: "127.0.0.1",
            CONF_TOKEN: _TOKEN,
            CONF_MAC: _MAC,
        },
        options={CONF_NOTIFY: True, CONF_VERSION: VERSION},
    )
    entry.add_to_hass(hass)
    return DreameVacuumDataUpdateCoordinator(hass, entry=entry)


async def test_a_device_thread_reads_the_entity_registry_on_the_loop(
    hass: HomeAssistant, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A property callback must not query the registry from the device thread."""
    coordinator = _coordinator(hass)
    seen: dict[str, int] = {}
    real = er.async_get

    def wrapped(hass_arg: HomeAssistant):
        seen["ident"] = threading.get_ident()
        return real(hass_arg)

    monkeypatch.setattr(er, "async_get", wrapped)
    worker = threading.Thread(
        target=lambda: coordinator._fire_event("warning", {"warning": "drop"})
    )
    worker.start()
    worker.join()
    await hass.async_block_till_done()

    assert seen["ident"] == hass.loop_thread_id


async def test_dismissing_a_warning_does_not_call_the_robot_on_the_loop(
    hass: HomeAssistant,
) -> None:
    """Clearing a warning is a device write. It must leave the event loop."""
    coordinator = _coordinator(hass)
    seen: dict[str, bool] = {}

    def clear_warning() -> None:
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            seen["on_loop"] = False
            return
        seen["on_loop"] = True

    coordinator._device.clear_warning = clear_warning
    coordinator._has_warning = True
    hass.data[persistent_notification.DOMAIN] = {}

    coordinator._notification_dismiss_listener(
        persistent_notification.UpdateType.REMOVED, {}
    )
    await hass.async_block_till_done()

    assert seen["on_loop"] is False

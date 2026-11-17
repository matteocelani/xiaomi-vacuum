"""The Dreame Vacuum component."""

from __future__ import annotations

from collections.abc import Mapping
import inspect
import warnings

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import CONF_DVC_KEY, DOMAIN

# Suppress python-miio FutureWarning on Python 3.13
warnings.filterwarnings(
    "ignore",
    category=FutureWarning,
    module="miio.miot_device",
)

# Suppress RuntimeWarning overflow encountered in scalar add
warnings.filterwarnings("ignore", category=RuntimeWarning)

from .coordinator import DreameVacuumDataUpdateCoordinator

PLATFORMS = (
    Platform.VACUUM,
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.SWITCH,
    Platform.BUTTON,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.CAMERA,
    Platform.TIME,
)


CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(_hass: HomeAssistant, _config: ConfigType) -> bool:
    """Set up the Dreame Vacuum integration."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Dreame Vacuum from a config entry."""

    coordinator = DreameVacuumDataUpdateCoordinator(hass, entry=entry)

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    # Set up all platforms for this device/entry.
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(update_listener))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Dreame Vacuum config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        coordinator: DreameVacuumDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
        if coordinator._unsub_dispatcher:
            coordinator._unsub_dispatcher()
            coordinator._unsub_dispatcher = None
        coordinator._device.listen(None)
        coordinator._device.listen_error(None)
        try:
            await hass.async_add_executor_job(coordinator._device.disconnect)
        finally:
            coordinator._device = None
            hass.data[DOMAIN].pop(entry.entry_id, None)

    return unload_ok


async def update_listener(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(config_entry.entry_id)


async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Drop the removed card license key from version 1 entries."""
    if config_entry.version != 1:
        return True
    _persist_migrated_entry(
        hass,
        config_entry,
        _without_card_license(config_entry.data),
        _without_card_license(config_entry.options),
    )
    return True


def _persist_migrated_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    data: dict[str, object],
    options: dict[str, object],
) -> None:
    """Store version 2. Home Assistant 2024.2 cannot pass version=."""
    update = hass.config_entries.async_update_entry
    if "version" in inspect.signature(update).parameters:
        update(config_entry, data=data, options=options, version=2)
        return
    config_entry.version = 2
    update(config_entry, data=data, options=options)


def _without_card_license(stored: Mapping[str, object]) -> dict[str, object]:
    return {key: value for key, value in stored.items() if key != CONF_DVC_KEY}

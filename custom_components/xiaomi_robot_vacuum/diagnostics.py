"""Diagnostics support for Dreame Vacuum."""

from __future__ import annotations

import base64
from datetime import date, datetime, timedelta
from enum import Enum
import traceback
from typing import Any

from homeassistant.components.diagnostics import REDACTED, async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_UNAVAILABLE, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .dreame import (
    DreameVacuumAutoSwitchProperty,
    DreameVacuumProperty,
    DreameVacuumStrAIProperty,
)

try:
    from homeassistant.helpers.device_registry import DeviceEntry
except ImportError:
    DeviceEntry = Any

# Keys whose values are credentials, device identity, or floor-plan geometry.
# async_redact_data matches these names on every nested dict.
TO_REDACT = {
    "FIRST_CONNECT_WIFI",
    "MATTER_QR_CODE",
    "SERIAL",
    "SERIAL_NUMBER",
    "WIFI_INFO",
    "WIFI_MAP",
    "access_token",
    "account",
    "active_areas",
    "active_cruise_points",
    "active_points",
    "ap",
    "auth_key",
    "bind_key",
    "ble_key",
    "captchaUrl",
    "captcha_url",
    "carpets",
    "center",
    "charger_position",
    "cookie",
    "cookies",
    "curtains",
    "cUserId",
    "deleted_carpets",
    "detected_carpets",
    "did",
    "dvc_key",
    "file_url",
    "furnitures",
    "host",
    "identity_session",
    "impassable_thresholds",
    "ip",
    "ip_address",
    "lat",
    "latitude",
    "local_ip",
    "localip",
    "lon",
    "longitude",
    "low_lying_areas",
    "mac",
    "mac_address",
    "map_data",
    "map_object_name",
    "map_url",
    "matter_qr_code",
    "no_go_areas",
    "no_mopping_areas",
    "notificationUrl",
    "object_name",
    "obstacles",
    "outline",
    "pass_token",
    "passToken",
    "passable_thresholds",
    "password",
    "path",
    "predefined_points",
    "ramps",
    "recovery_map_list",
    "refresh_token",
    "robot_position",
    "rooms",
    "router_position",
    "secondary_key",
    "serial",
    "serial_number",
    "service_token",
    "serviceToken",
    "session",
    "small_path",
    "ssecurity",
    "token",
    "uid",
    "url",
    "user_id",
    "userId",
    "username",
    "vacuum_position",
    "verification_url",
    "virtual_thresholds",
    "virtual_walls",
    "wifi_map",
    "yetAnotherServiceToken",
}


def _get(target: Any, name: str, default: Any = None) -> Any:
    if target is None:
        return default
    try:
        return getattr(target, name, default)
    except Exception as ex:
        return f"<{type(ex).__name__}: {ex}>"


def _sanitize(value: Any, seen: set[int] | None = None) -> Any:
    if isinstance(value, Enum):
        value = value.value if isinstance(value.value, (bool, int, float, str)) else value.name
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, (bytes, bytearray)):
        return base64.b64encode(bytes(value)).decode("ascii")
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, timedelta):
        return str(value)
    if seen is None:
        seen = set()
    marker = id(value)
    if marker in seen:
        return f"<recursive {type(value).__name__}>"
    seen.add(marker)
    try:
        if isinstance(value, dict):
            return {str(k): _sanitize(v, seen) for k, v in value.items()}
        if isinstance(value, (list, tuple, set, frozenset)):
            return [_sanitize(v, seen) for v in value]
        as_dict = getattr(value, "as_dict", None)
        if callable(as_dict):
            try:
                return _sanitize(as_dict(), seen)
            except Exception:
                pass
        if hasattr(value, "__dict__"):
            return {
                k: _sanitize(v, seen)
                for k, v in vars(value).items()
                if not k.startswith("_")
            }
    finally:
        seen.discard(marker)
    return repr(value)


def _entities(
    hass: HomeAssistant, entry: ConfigEntry, device: Any, device_id: str | None = None
) -> dict[str, Any]:
    mirrors: dict[str, Any] = {}
    data = _get(device, "data")
    if isinstance(data, dict):
        names = {prop.value: prop.name.lower() for prop in DreameVacuumProperty}
        for did, value in data.items():
            did_value = did.value if isinstance(did, Enum) else did
            if did_value in names:
                mirrors[names[did_value]] = value
    for source in ("auto_switch_data", "ai_data"):
        parsed = _get(device, source)
        if isinstance(parsed, dict):
            for key, value in parsed.items():
                mirrors[str(key).lower()] = value
    capability_list = _get(_get(device, "capability"), "list")
    status = _get(device, "status")
    status_type = type(status)
    component = (hass.data.get("entity_components") or {}).get(Platform.VACUUM)
    registry = er.async_get(hass)
    entries_for_config_entry = getattr(er, "async_entries_for_config_entry", None)
    if entries_for_config_entry is not None:
        registry_entries = entries_for_config_entry(registry, entry.entry_id)
    else:
        registry_entries = [
            registry_entry
            for registry_entry in registry.entities.values()
            if registry_entry.config_entry_id == entry.entry_id
        ]
    vacuum: dict[str, Any] = {}
    disabled: list[str] = []
    availability: dict[str, bool] = {}
    for registry_entry in registry_entries:
        if device_id is not None and registry_entry.device_id != device_id:
            continue
        if _get(registry_entry, "disabled_by") is not None or _get(registry_entry, "hidden_by") is not None:
            disabled.append(registry_entry.entity_id)
            continue
        state = hass.states.get(registry_entry.entity_id)
        usable = state is not None and state.state != STATE_UNAVAILABLE
        availability[registry_entry.entity_id] = usable
        if usable and registry_entry.entity_id.split(".")[0] == Platform.VACUUM:
            attributes = _get(
                component.get_entity(registry_entry.entity_id) if component is not None else None,
                "extra_state_attributes",
            )
            if not isinstance(attributes, dict):
                own = set(_get(status, "attributes") or {})
                attributes = {k: v for k, v in state.attributes.items() if k in own}
            computed: dict[str, Any] = {"entity_id": registry_entry.entity_id}
            for key, value in attributes.items():
                if key.endswith("_list"):
                    continue
                if isinstance(value, str) and hasattr(status_type, f"{key}_name"):
                    continue
                if capability_list is not None and value == capability_list:
                    continue
                mirror = mirrors.get(key)
                if mirror is not None:
                    if type(value) is type(mirror) and value == mirror:
                        continue
                    if (
                        isinstance(value, bool)
                        and isinstance(mirror, int)
                        and not isinstance(mirror, bool)
                        and value == (mirror > 0)
                    ):
                        continue
                computed[key] = value
            vacuum = computed
    details: dict[str, Any] = {}
    if vacuum:
        details["vacuum"] = vacuum
    if disabled:
        details["disabled"] = disabled
    if availability:
        details["availability"] = availability
    return details


def _capabilities(device: Any) -> list[str] | None:
    capability = _get(device, "capability")
    if capability is None:
        return None
    return sorted(
        name.upper()
        for name in dir(capability)
        if not name.startswith("_") and _get(capability, name) is True
    )


def _device_details(device: Any) -> dict[str, Any] | None:
    if device is None:
        return None
    return {
        "model": _get(_get(device, "info"), "model"),
        "serial_number": _get(_get(device, "status"), "serial_number"),
    }


def _properties(device: Any) -> dict[str, Any] | None:
    data = _get(device, "data")
    if not isinstance(data, dict):
        return None
    requested = {prop.value for prop in (_get(device, "_default_properties") or DreameVacuumProperty)}
    packed = tuple(
        f'"{prop.value}"'
        for group in (DreameVacuumAutoSwitchProperty, DreameVacuumStrAIProperty)
        for prop in group
        if isinstance(prop.value, str)
    )
    names = {prop.value: prop.name for prop in DreameVacuumProperty}
    properties: dict[str, Any] = {}
    for did, value in data.items():
        did_value = did.value if isinstance(did, Enum) else did
        if did_value not in requested:
            continue
        if isinstance(value, str) and any(
            key in value for key in ('"object_name"', '"mapobj"', *packed)
        ):
            continue
        if isinstance(did_value, int):
            properties[names.get(did_value, f"UNKNOWN_{did_value}")] = value
        else:
            properties[str(did_value)] = value
    for source in ("auto_switch_data", "ai_data"):
        parsed = _get(device, source)
        if isinstance(parsed, dict):
            properties.update(parsed)
    return dict(sorted(properties.items()))


def _entry_details(entry: ConfigEntry) -> dict[str, Any]:
    return {
        "data": dict(entry.data),
        "options": dict(_get(entry, "options") or {}),
    }


def _failure(ex: Exception) -> dict[str, Any]:
    return {
        "diagnostics_error": f"{type(ex).__name__}: {ex}",
        "diagnostics_traceback": traceback.format_exc().splitlines(),
    }


def _section(builder: Any, *args: Any) -> Any:
    try:
        return _sanitize(builder(*args))
    except Exception as ex:
        return _failure(ex)


def _is_sensitive_string(value: str) -> bool:
    """A signed cloud URL carries the query that opens the file."""
    return "://" in value and "?" in value


def _scrub_sensitive_strings(value: object) -> object:
    if isinstance(value, str):
        if _is_sensitive_string(value):
            return REDACTED
        return value
    if isinstance(value, dict):
        return {key: _scrub_sensitive_strings(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_scrub_sensitive_strings(item) for item in value]
    return value


def redact_diagnostics(value: object) -> object:
    """Mask secrets and floor-plan fields on a JSON-ready diagnostics payload."""
    sanitized = _sanitize(value)
    if not isinstance(sanitized, dict):
        return _scrub_sensitive_strings(sanitized)
    return _scrub_sensitive_strings(async_redact_data(sanitized, TO_REDACT))


async def _async_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry, device_id: str | None = None
) -> dict[str, object]:
    coordinator = (hass.data.get(DOMAIN) or {}).get(entry.entry_id)
    device = _get(coordinator, "device")
    payload = {
        "generated_at": dt_util.utcnow().isoformat(),
        "device": _section(_device_details, device),
        "entry": _section(_entry_details, entry),
        "capabilities": _section(_capabilities, device),
        "properties": _section(_properties, device),
        "entities": _section(_entities, hass, entry, device, device_id),
    }
    redacted = redact_diagnostics(payload)
    if isinstance(redacted, dict):
        return redacted
    return {"diagnostics_error": "redaction failed"}


async def async_get_config_entry_diagnostics(hass: HomeAssistant, entry: ConfigEntry) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    return await _async_diagnostics(hass, entry)


async def async_get_device_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry, device: DeviceEntry
) -> dict[str, Any]:
    """Return diagnostics for a device."""
    return await _async_diagnostics(hass, entry, device.id)

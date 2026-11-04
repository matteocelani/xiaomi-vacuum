"""Dump Dreame-model behavior for one checkout of this integration."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import logging
from pathlib import Path
import sys
from types import SimpleNamespace
import zlib

_GZIP_WINDOW_BITS = zlib.MAX_WBITS | 32
_STRING_FLAGS = ("0", "1", "2", "no", "")
_NUMBER_FLAGS = (None, False, True, 0, 1, 2, 0.0, 0.5)
_GROUP_VALUES = (None, 0, 1, 255, 65535, 0x010203, -1)


def main() -> None:
    """Write one checkout's Dreame behavior snapshot as JSON."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    root = Path(args.root).resolve()
    # The checkout is chosen by the caller. Import that tree, not whatever
    # directory the harness itself lives in.
    sys.path = [str(root), *[entry for entry in sys.path if entry not in ("", ".")]]
    logging.disable(logging.CRITICAL)
    payload = _snapshot()
    Path(args.output).write_text(json.dumps(payload), encoding="utf-8")


def _snapshot() -> dict[str, object]:
    from custom_components.dreame_vacuum.dreame.const import (
        DEVICE_INFO,
        ERROR_CODE_TO_ERROR_NAME,
    )
    from custom_components.dreame_vacuum.dreame.device import (
        DreameVacuumDevice,
        DreameVacuumDeviceStatus,
    )
    from custom_components.dreame_vacuum.dreame.protocol import (
        DreameVacuumDeviceProtocol,
    )
    from custom_components.dreame_vacuum.dreame.types import (
        DreameVacuumAction,
        DreameVacuumActionMapping,
        DreameVacuumProperty,
        DreameVacuumPropertyMapping,
    )

    decoded = _decode(DEVICE_INFO)
    descriptions = _descriptions()
    saturated = {prop.value: 1 for prop in DreameVacuumProperty}
    auto_switch, ai_data = _side_data()
    catalog_ids = _catalog_ids()
    models: dict[str, object] = {}
    records = decoded[0]
    model_index = decoded[3]
    if not isinstance(records, list) or not isinstance(model_index, dict):
        raise TypeError("device catalog is missing a section")
    for code, record_index in model_index.items():
        if not isinstance(record_index, int) or not 0 <= record_index < len(records):
            continue
        record = records[record_index]
        brand = record[0] if isinstance(record, list) and record else None
        model_id = _historical_model_id(brand, code)
        models[model_id] = _model_snapshot(
            model_id,
            code,
            decoded,
            descriptions,
            saturated,
            auto_switch,
            ai_data,
            catalog_ids.get(str(code)),
        )
    return {
        "models": models,
        "device": _device_snapshot(
            DreameVacuumDevice,
            DreameVacuumDeviceStatus,
            DreameVacuumDeviceProtocol,
            DreameVacuumProperty,
            DreameVacuumAction,
            DreameVacuumPropertyMapping,
            DreameVacuumActionMapping,
            ERROR_CODE_TO_ERROR_NAME,
        ),
    }


def _model_snapshot(
    model_id: str,
    code: object,
    decoded: list[object],
    descriptions: list[tuple[str, object]],
    saturated: dict[int, int],
    auto_switch: dict[str, int],
    ai_data: dict[str, object],
    catalog_model_id: str | None,
) -> dict[str, object]:
    from custom_components.dreame_vacuum.dreame.types import (
        DreameVacuumDeviceCapability,
    )

    entry = _entry(decoded, code)
    empty = _load(DreameVacuumDeviceCapability, model_id, decoded, {}, None, None)
    reported = _load(
        DreameVacuumDeviceCapability,
        model_id,
        decoded,
        saturated,
        auto_switch,
        ai_data,
    )
    empty_cloud = _load(
        DreameVacuumDeviceCapability,
        model_id,
        decoded,
        {},
        None,
        None,
        map_manager=object(),
    )
    reported_cloud = _load(
        DreameVacuumDeviceCapability,
        model_id,
        decoded,
        saturated,
        auto_switch,
        ai_data,
        map_manager=object(),
    )
    family = _family_touch(catalog_model_id or model_id)
    return {
        "entry": entry,
        "catalog_model_id": catalog_model_id,
        "family": family,
        "fault_override": _fault_override(family),
        "xiaomi_controls": _xiaomi_control_count(family),
        "empty": empty,
        "reported": reported,
        "entities_empty": _entities(descriptions, empty, {}, None, None),
        "entities_reported": _entities(
            descriptions, reported, saturated, auto_switch, ai_data
        ),
        "entities_empty_cloud": _entities(descriptions, empty_cloud, {}, None, None),
        "entities_reported_cloud": _entities(
            descriptions, reported_cloud, saturated, auto_switch, ai_data
        ),
    }


def _entry(decoded: list[object], code: object) -> dict[str, object]:
    records = decoded[0]
    capabilities = decoded[1]
    keys = decoded[2]
    model_index = decoded[3]
    if (
        not isinstance(records, list)
        or not isinstance(capabilities, list)
        or not isinstance(keys, list)
        or not isinstance(model_index, dict)
    ):
        return {"error": "catalog shape"}
    record_index = model_index.get(code)
    if not isinstance(record_index, int) or not 0 <= record_index < len(records):
        return {"error": "record index"}
    record = records[record_index]
    capability = None
    key_hash = None
    if (
        isinstance(record, list)
        and len(record) >= 3
        and isinstance(record[2], int)
        and 0 <= record[2] < len(capabilities)
    ):
        capability = capabilities[record[2]]
    if (
        isinstance(record, list)
        and len(record) == 4
        and isinstance(record[3], int)
        and 0 <= record[3] < len(keys)
        and isinstance(keys[record[3]], str)
    ):
        key_hash = hashlib.sha256(keys[record[3]].encode()).hexdigest()
    return {
        "record": json.dumps(record, separators=(",", ":")),
        "capability": json.dumps(capability, separators=(",", ":")),
        "key_sha256": key_hash,
    }


def _load(
    capability_type: type,
    model_id: str,
    decoded: list[object],
    data: dict[int, int],
    auto_switch: dict[str, int] | None,
    ai_data: dict[str, object] | None,
    map_manager: object | None = None,
) -> dict[str, object]:

    host = _Host(model_id, data, auto_switch, ai_data, map_manager)
    capability = capability_type(host)
    host.capability = capability
    loaded, failure = _guard(lambda: capability.load(decoded))
    if not loaded:
        return {"error": failure}
    attrs = {}
    for name, value in vars(capability).items():
        if name.startswith("_") or name in {"list", "key"}:
            continue
        attrs[name] = _plain(value)
    key = capability.key
    return {
        "flags": sorted(capability.list),
        "attrs": attrs,
        "key_sha256": (
            hashlib.sha256(key.encode()).hexdigest() if isinstance(key, str) else None
        ),
        "map": bool(capability.map),
    }


class _Host:
    """Enough of a device for capability.load to read properties and status."""

    def __init__(
        self,
        model_id: str,
        data: dict[int, int],
        auto_switch: dict[str, int] | None,
        ai_data: dict[str, object] | None,
        map_manager: object | None,
    ) -> None:
        self.info = SimpleNamespace(model=model_id, version=1)
        self.data = data
        self.auto_switch_data = auto_switch
        self.ai_data = ai_data
        self._map_manager = map_manager
        self._property_codec = None
        self.status = SimpleNamespace(
            current_segments=None,
            current_map=None,
            selected_map=None,
            fill_light=None,
        )
        self.capability = None

    def get_property(self, prop: object) -> object:
        from custom_components.dreame_vacuum.dreame.device import DreameVacuumDevice

        return DreameVacuumDevice.get_property(self, prop)

    def get_auto_switch_property(self, prop: object) -> object:
        from custom_components.dreame_vacuum.dreame.device import DreameVacuumDevice

        return DreameVacuumDevice.get_auto_switch_property(self, prop)

    def get_ai_property(self, prop: object) -> object:
        from custom_components.dreame_vacuum.dreame.device import DreameVacuumDevice

        return DreameVacuumDevice.get_ai_property(self, prop)


def _entities(
    descriptions: list[tuple[str, object]],
    loaded: dict[str, object],
    data: dict[int, int],
    auto_switch: dict[str, int] | None,
    ai_data: dict[str, object] | None,
) -> list[str]:
    if "error" in loaded:
        return [f"load:{loaded['error']}"]
    device = _EntityDevice(loaded, data, auto_switch, ai_data)
    created: list[str] = []
    for domain, description in descriptions:
        if domain == "camera" and not device.capability.map:
            continue
        exists = getattr(description, "exists_fn", None)
        if exists is None:
            created.append(f"{domain}:{_entity_key(description)}")
            continue
        loaded, present = _guard(
            lambda exists=exists, description=description, device=device: bool(
                exists(description, device)
            )
        )
        if not loaded:
            created.append(f"{domain}:{_entity_key(description)}:error:{present}")
            continue
        if present:
            created.append(f"{domain}:{_entity_key(description)}")
    created.sort()
    return created


class _EntityDevice:
    """Mapping, data, and capability values an exists_fn is allowed to read."""

    def __init__(
        self,
        loaded: dict[str, object],
        data: dict[int, int],
        auto_switch: dict[str, int] | None,
        ai_data: dict[str, object] | None,
    ) -> None:
        from custom_components.dreame_vacuum.dreame.types import (
            DreameVacuumActionMapping,
            DreameVacuumPropertyMapping,
        )

        self.data = data
        self.auto_switch_data = auto_switch
        self.ai_data = ai_data
        self.property_mapping = DreameVacuumPropertyMapping
        self.action_mapping = DreameVacuumActionMapping
        self._property_codec = None
        self.capability = _CapabilityView(loaded)
        self.status = _Soft()


class _CapabilityView:
    """Attribute view of one loaded capability, including map."""

    def __init__(self, loaded: dict[str, object]) -> None:
        attrs = loaded.get("attrs")
        self._attrs = attrs if isinstance(attrs, dict) else {}
        self.map = bool(loaded.get("map"))
        flags = loaded.get("flags")
        self._flags = set(flags) if isinstance(flags, list) else set()

    def __getattr__(self, name: str) -> object:
        if name in self._attrs:
            return self._attrs[name]
        return name in self._flags


class _Soft:
    """Missing status attributes stay unset instead of raising."""

    def __getattr__(self, name: str) -> None:
        if name.startswith("_"):
            raise AttributeError(name)
        return


def _descriptions() -> list[tuple[str, object]]:
    import importlib

    found: list[tuple[str, object]] = []
    modules = (
        ("binary_sensor", "BINARY_SENSORS"),
        ("button", "BUTTONS"),
        ("camera", "CAMERAS"),
        ("number", "NUMBERS"),
        ("select", "SELECTS"),
        ("sensor", "SENSORS"),
        ("switch", "SWITCHES"),
        ("time", "TIMES"),
    )
    for module_name, attribute in modules:
        module = importlib.import_module(
            f"custom_components.dreame_vacuum.{module_name}"
        )
        descriptions = getattr(module, attribute)
        for description in descriptions:
            found.append((module_name, description))
    return found


def _family_touch(model_id: str) -> dict[str, object]:
    from custom_components.dreame_vacuum.dreame.device import DreameVacuumDevice
    from custom_components.dreame_vacuum.dreame.types import (
        DreameVacuumActionMapping,
        DreameVacuumPropertyMapping,
    )

    if not hasattr(DreameVacuumDevice, "_apply_reported_family"):
        return {"hook": False, "applied": False, "mapping_replaced": False}
    device = object.__new__(DreameVacuumDevice)
    device._family_resolver = _resolver()
    device._property_codec = None
    device.info = SimpleNamespace(model=model_id)
    device.host = ""
    device.token = ""
    device._map_manager = None
    device._protocol = SimpleNamespace(property_transport=None)
    device.capability = SimpleNamespace(loaded=False)
    device.property_mapping = DreameVacuumPropertyMapping
    device.action_mapping = DreameVacuumActionMapping
    DreameVacuumDevice._apply_reported_family(device)
    return {
        "hook": True,
        "applied": device._property_codec is not None,
        "mapping_replaced": device.property_mapping is not DreameVacuumPropertyMapping,
    }


def _resolver() -> object:
    try:
        from custom_components.dreame_vacuum.xiaomi import resolve_family
    except ImportError:
        return lambda _model: None
    return resolve_family


def _fault_override(family: dict[str, object]) -> str | None:
    if family.get("applied") is not True:
        try:
            from custom_components.dreame_vacuum.dreame.family_codec import (
                family_fault_name,
            )
        except ImportError:
            return None
        return family_fault_name(SimpleNamespace(_property_codec=None), 2)
    return "family-applied"


def _xiaomi_control_count(family: dict[str, object]) -> int:
    if family.get("applied") is True:
        return -1
    try:
        from custom_components.dreame_vacuum.xiaomi import controls_of
    except ImportError:
        return 0
    return len(controls_of(SimpleNamespace(_property_codec=None)))


def _catalog_ids() -> dict[str, str]:
    try:
        from custom_components.dreame_vacuum.dreame.catalog import load_model_catalog
        from custom_components.dreame_vacuum.dreame.const import DEVICE_INFO
    except ImportError:
        return {}
    return {
        model_id.rpartition(".")[2]: model_id
        for model_id in load_model_catalog(DEVICE_INFO)
    }


def _device_snapshot(
    device_type: type,
    status_type: type,
    protocol_type: type,
    property_type: type,
    action_type: type,
    property_mapping: dict[object, dict[str, int]],
    action_mapping: dict[object, dict[str, int]],
    error_names: dict[object, str],
) -> dict[str, object]:
    from custom_components.dreame_vacuum.dreame.types import DID

    protocol = protocol_type("127.0.0.1", "00" * 16)
    return {
        "property_enum": list(property_type.__members__),
        "action_enum": list(action_type.__members__),
        "property_mapping": _mapping(property_mapping),
        "action_mapping": _mapping(action_mapping),
        "did": _did_names(DID, property_mapping),
        "error_names": {code.name: error_names[code] for code in error_names},
        "error_name_path": _error_name_path(status_type),
        "group_values": _group_values(device_type),
        "cleaning_paused": _cleaning_paused(status_type),
        "positive_flags": _positive_flags(),
        "parsers": _parsers(device_type),
        "map_actions": _map_actions(),
        "miio_timeout": getattr(protocol, "_timeout", None),
        "property_transport": getattr(protocol, "property_transport", None),
    }


def _mapping(mapping: dict[object, dict[str, int]]) -> dict[str, dict[str, int]]:
    rendered: dict[str, dict[str, int]] = {}
    for prop, entry in mapping.items():
        rendered[prop.name] = dict(entry)
    return rendered


def _did_names(
    did: object,
    mapping: dict[object, dict[str, int]],
) -> list[str]:
    found: list[str] = []
    for prop, entry in mapping.items():
        resolved = did(entry["siid"], entry["piid"])
        name = resolved.name if resolved is not None else None
        found.append(f"{entry['siid']}.{entry['piid']}={name}|declared:{prop.name}")
    return found


def _error_name_path(status_type: type) -> dict[str, str]:
    from custom_components.dreame_vacuum.dreame.types import DreameVacuumErrorCode

    status = object.__new__(status_type)
    status._device = SimpleNamespace(
        get_property=lambda _prop: None,
        capability=SimpleNamespace(self_wash_base=False, gen5=False),
        _property_codec=None,
        _map_manager=None,
    )
    names: dict[str, str] = {}
    for code in DreameVacuumErrorCode:
        status.faults = [code.value]
        loaded, name = _guard(lambda status=status: status.error_name)
        names[code.name] = name if loaded else f"error:{name}"
    return names


def _group_values(device_type: type) -> list[object]:
    rendered: list[object] = []
    for value in _GROUP_VALUES:
        parts = device_type.split_group_value(value)
        rendered.append(
            {
                "value": value,
                "parts": parts,
                "combined": device_type.combine_group_value(parts) if parts else None,
            }
        )
    return rendered


def _cleaning_paused(status_type: type) -> dict[str, object]:
    rendered: dict[str, object] = {}
    for value in (*_NUMBER_FLAGS, *_STRING_FLAGS):
        status = object.__new__(status_type)
        status._device = SimpleNamespace(
            get_property=lambda _prop, current=value: current
        )
        loaded, paused = _guard(lambda status=status: status.cleaning_paused)
        rendered[_token(value)] = paused if loaded else f"error:{paused}"
    return rendered


def _positive_flags() -> dict[str, object]:
    try:
        from custom_components.dreame_vacuum.dreame.device import _is_positive_value
    except ImportError:
        _is_positive_value = None
    rendered: dict[str, object] = {}
    for value in (*_NUMBER_FLAGS, *_STRING_FLAGS):
        if _is_positive_value is None:
            loaded, result = _guard(lambda value=value: bool(value > 0))
        else:
            loaded, result = _guard(lambda value=value: _is_positive_value(value))
        rendered[_token(value)] = result if loaded else f"error:{result}"
    return rendered


def _parsers(device_type: type) -> dict[str, object]:
    schedule = "1-1-08:00-1111111-1-0-1-2-0"
    dnd = json.dumps(
        [{"id": 2, "en": True, "st": "22:00", "et": "07:00", "wk": 127, "ss": 0}]
    )
    stream = json.dumps(
        {"result": 0, "session": "s", "operType": "end", "operation": "end"}
    )
    off_peak = json.dumps({"enable": True, "startTime": "22:00", "endTime": "08:00"})
    return {
        "schedule_string": _run_parser(
            device_type, "_schedule_changed", "SCHEDULE", schedule
        ),
        "schedule_number": _run_parser(
            device_type, "_schedule_changed", "SCHEDULE", 19
        ),
        "dnd_string": _run_parser(device_type, "_dnd_task_changed", "DND_TASK", dnd),
        "dnd_number": _run_parser(device_type, "_dnd_task_changed", "DND_TASK", 1),
        "stream_string": _run_parser(
            device_type, "_stream_status_changed", "STREAM_STATUS", stream
        ),
        "stream_number": _run_parser(
            device_type, "_stream_status_changed", "STREAM_STATUS", 1
        ),
        "off_peak_string": _run_parser(
            device_type, "_off_peak_charging_changed", "OFF_PEAK_CHARGING", off_peak
        ),
        "off_peak_number": _run_parser(
            device_type, "_off_peak_charging_changed", "OFF_PEAK_CHARGING", 1
        ),
    }


def _run_parser(
    device_type: type, method_name: str, property_name: str, value: object
) -> object:
    from custom_components.dreame_vacuum.dreame.types import DreameVacuumProperty

    device = object.__new__(device_type)
    device.data = {getattr(DreameVacuumProperty, property_name).value: value}
    device.status = SimpleNamespace(
        schedule=None,
        dnd_tasks=None,
        stream_session=None,
        stream_status=None,
        off_peak_charging_config=None,
    )
    loaded, failure = _guard(lambda: getattr(device_type, method_name)(device))
    if not loaded:
        return {"error": failure}
    return {
        "schedule": _plain_tasks(device.status.schedule),
        "dnd": _plain_tasks(device.status.dnd_tasks),
        "stream_session": device.status.stream_session,
        "stream_status": _plain(device.status.stream_status),
        "off_peak": _plain(device.status.off_peak_charging_config),
    }


def _map_actions() -> dict[str, object]:
    from custom_components.dreame_vacuum.dreame.map import DreameMapVacuumMapManager
    from custom_components.dreame_vacuum.dreame.types import (
        DreameVacuumAction,
        DreameVacuumActionMapping,
    )

    rendered: dict[str, object] = {}
    for action_name in ("REQUEST_MAP", "WIFI_MAP"):
        action = getattr(DreameVacuumAction, action_name)
        if hasattr(DreameMapVacuumMapManager, "_mapped_action"):
            manager = object.__new__(DreameMapVacuumMapManager)
            manager.action_mapping = None
            mapping = manager._mapped_action(action)
        else:
            mapping = DreameVacuumActionMapping[action]
        rendered[action_name] = dict(mapping) if isinstance(mapping, dict) else None
    return rendered


def _side_data() -> tuple[dict[str, int], dict[str, object]]:
    from custom_components.dreame_vacuum.dreame.types import (
        DreameVacuumAIProperty,
        DreameVacuumAutoSwitchProperty,
        DreameVacuumStrAIProperty,
    )

    auto_switch = {item.name: 1 for item in DreameVacuumAutoSwitchProperty}
    ai_data: dict[str, object] = {item.name: True for item in DreameVacuumAIProperty}
    ai_data.update({item.name: "value" for item in DreameVacuumStrAIProperty})
    return auto_switch, ai_data


def _plain_tasks(tasks: object) -> object:
    if not isinstance(tasks, list):
        return _plain(tasks)
    return [_plain(task) for task in tasks]


def _plain(value: object) -> object:
    if value is None or isinstance(value, str | int | float | bool):
        if isinstance(value, str) and len(value) > 32:
            return {"sha256": hashlib.sha256(value.encode()).hexdigest()}
        return value
    if isinstance(value, list | tuple):
        return [_plain(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _plain(item) for key, item in value.items()}
    as_dict = getattr(value, "as_dict", None)
    if callable(as_dict):
        return _plain(as_dict())
    name = getattr(value, "name", None)
    if isinstance(name, str) and not callable(name):
        return name
    return type(value).__name__


def _token(value: object) -> str:
    return "none" if value is None else json.dumps(value)


def _historical_model_id(brand: object, code: object) -> str:
    if brand == 1:
        prefix = "xiaomi"
    elif brand == 2:
        prefix = "mova"
    elif brand == 3:
        prefix = "trouver"
    else:
        prefix = "dreame"
    return f"{prefix}.vacuum.{code}"


def _guard(action: object) -> tuple[bool, object]:
    """Run an action and keep the exception type when the two trees disagree."""
    if not callable(action):
        raise TypeError("snapshot action is not callable")
    try:
        return True, action()
    except Exception as exc:  # noqa: BLE001 - golden diff records the exception type
        return False, type(exc).__name__


def _decode(blob: str) -> list[object]:
    decoded = json.loads(zlib.decompress(base64.b64decode(blob), _GZIP_WINDOW_BITS))
    if isinstance(decoded, list):
        return decoded
    raise TypeError("device catalog is not a list")


def _entity_key(description: object) -> str:
    key = getattr(description, "key", None)
    if isinstance(key, str) and key:
        return key
    prop = getattr(description, "property_key", None)
    prop_name = getattr(prop, "name", None)
    if isinstance(prop_name, str):
        return prop_name.lower()
    action = getattr(description, "action_key", None)
    action_name = getattr(action, "name", None)
    if isinstance(action_name, str):
        return action_name.lower()
    name = getattr(description, "name", None)
    if isinstance(name, str):
        return name.lower().replace(" ", "_")
    return "unnamed"


if __name__ == "__main__":
    main()

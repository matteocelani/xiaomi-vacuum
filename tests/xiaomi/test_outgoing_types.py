"""Every family rejects values and action inputs the spec does not publish."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from custom_components.dreame_vacuum.dreame.device import DreameVacuumDevice
from custom_components.dreame_vacuum.dreame.exceptions import (
    InvalidActionException,
    InvalidValueException,
)
from custom_components.dreame_vacuum.dreame.types import (
    DreameVacuumAction,
    DreameVacuumProperty,
)
from custom_components.dreame_vacuum.xiaomi.exceptions import XiaomiValueException
from custom_components.dreame_vacuum.xiaomi.mapping import _FAMILIES
from custom_components.dreame_vacuum.xiaomi.value_limits import wire_kind
import pytest

_SPECS = Path(__file__).parent / "specs"
_INT_FORMATS = frozenset(
    {"uint8", "uint16", "uint32", "int8", "int16", "int32", "int64"}
)
_BAD_INT = (101.0, "101", [1, 2], None, True, False)
_BAD_BOOL = (101.0, "101", [1, 2], None, 2)
_BAD_STRING = (None, [1, 2], True, 1, 101.0, "101")


def _spec(model: str) -> dict[str, object]:
    suffix = model.rsplit(".", 1)[-1]
    loaded = json.loads((_SPECS / f"{suffix}.json").read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _kind(fmt: object) -> str:
    if fmt in _INT_FORMATS:
        return "int"
    if fmt in {"bool", "string", "float"}:
        assert isinstance(fmt, str)
        return fmt
    raise AssertionError(fmt)


def _properties(
    document: dict[str, object],
) -> dict[tuple[int, int], dict[str, object]]:
    found: dict[tuple[int, int], dict[str, object]] = {}
    services = document["services"]
    assert isinstance(services, list)
    for service in services:
        assert isinstance(service, dict)
        siid = service["iid"]
        assert isinstance(siid, int)
        raw = service.get("properties") or []
        assert isinstance(raw, list)
        for prop in raw:
            assert isinstance(prop, dict)
            piid = prop["iid"]
            assert isinstance(piid, int)
            found[(siid, piid)] = prop
    return found


def _action_inputs(document: dict[str, object], siid: int, aiid: int) -> frozenset[int]:
    services = document["services"]
    assert isinstance(services, list)
    for service in services:
        assert isinstance(service, dict)
        if service["iid"] != siid:
            continue
        raw = service.get("actions") or []
        assert isinstance(raw, list)
        for action in raw:
            assert isinstance(action, dict)
            if action["iid"] != aiid:
                continue
            declared = action.get("in") or []
            assert isinstance(declared, list)
            return frozenset(item for item in declared if isinstance(item, int))
    raise AssertionError((siid, aiid))


@pytest.mark.parametrize("model", sorted(_FAMILIES))
def test_outgoing_types_follow_the_spec_for_every_family(model: str) -> None:
    family = _FAMILIES[model]
    assert wire_kind("missing.model", "VOLUME") is None
    assert wire_kind(model, "NOT_A_PROPERTY") is None
    props = _properties(_spec(model))
    device = object.__new__(DreameVacuumDevice)
    device._property_codec = family
    device._commands_fail_closed = False
    device.schedule_update = lambda *_args, **_kwargs: None
    device.property_mapping = {
        DreameVacuumProperty[name]: dict(address)
        for name, address in family.property_overrides.items()
    }
    device.action_mapping = {}
    sent: list[object] = []
    device._protocol = SimpleNamespace(
        send=lambda *_args, **_kwargs: sent.append(True) or {"ok": True}
    )
    for name, address in family.property_overrides.items():
        spec = props[(address["siid"], address["piid"])]
        kind = _kind(spec.get("format"))
        assert wire_kind(model, name) == kind
        if kind == "int":
            bad_values: tuple[object, ...] = _BAD_INT
            if name not in {"STATE", "TASK_STATUS"}:
                sample = _int_sample(spec)
                if sample is not None:
                    assert isinstance(family.convert_outgoing(name, sample), int)
        elif kind == "bool":
            bad_values = _BAD_BOOL
            assert family.convert_outgoing(name, True) is True
            assert family.convert_outgoing(name, 0) == 0
        else:
            bad_values = _BAD_STRING
            assert family.convert_outgoing(name, "1-2-3") == "1-2-3"
        for value in bad_values:
            with pytest.raises(XiaomiValueException):
                family.convert_outgoing(name, value)
        if name in {"VOLUME", "STATE"}:
            with pytest.raises(InvalidValueException):
                device.send_command(
                    "set_properties",
                    [
                        {
                            "siid": address["siid"],
                            "piid": address["piid"],
                            "value": "101" if name == "VOLUME" else True,
                        }
                    ],
                )
    assert sent == []


def _int_sample(spec: dict[str, object]) -> int | None:
    listed = spec.get("value-list")
    if isinstance(listed, list):
        for item in listed:
            if isinstance(item, dict) and isinstance(item.get("value"), int):
                return item["value"]
    bounds = spec.get("value-range")
    if isinstance(bounds, list) and bounds and isinstance(bounds[0], int):
        return bounds[0]
    return None


@pytest.mark.parametrize("model", sorted(_FAMILIES))
def test_action_inputs_follow_the_spec_for_every_family(model: str) -> None:
    family = _FAMILIES[model]
    document = _spec(model)
    device = object.__new__(DreameVacuumDevice)
    device._property_codec = family
    device._commands_fail_closed = False
    device.schedule_update = lambda *_args, **_kwargs: None
    device.property_mapping = {
        DreameVacuumProperty[name]: dict(address)
        for name, address in family.property_overrides.items()
    }
    device.action_mapping = {
        DreameVacuumAction[name]: dict(address)
        for name, address in family.action_overrides.items()
    }
    sent: list[object] = []
    device._protocol = SimpleNamespace(
        send=lambda *_args, **_kwargs: sent.append(True) or {"ok": True}
    )
    for _name, address in family.action_overrides.items():
        siid = address["siid"]
        aiid = address["aiid"]
        declared = _action_inputs(document, siid, aiid)
        assert family.declared_inputs(siid, aiid) == declared
        for piid in (1, 2, 3):
            if piid in declared:
                continue
            with pytest.raises(InvalidActionException):
                device.send_command(
                    "action",
                    {
                        "siid": siid,
                        "aiid": aiid,
                        "in": [{"piid": piid, "value": "anything"}],
                    },
                )
    assert sent == []

"""Spec-generated writes for the approved entities and the schedule service."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from custom_components.dreame_vacuum.xiaomi.controls import write_control
from custom_components.dreame_vacuum.xiaomi.exceptions import XiaomiControlException
from custom_components.dreame_vacuum.xiaomi.mapping import resolve_family
from custom_components.dreame_vacuum.xiaomi.schedule import (
    SCHEDULE_MODELS,
    add_schedule,
)
import pytest
from tests.xiaomi.deep.cases import property_cases
from tests.xiaomi.deep.corpus import manifest_models

_PLAN = "docs/unmapped-props-plan.md"
_LAYOUT_MODELS = frozenset(
    {
        "mijia.vacuum.b108za",
        "mijia.vacuum.b108zb",
        "mijia.vacuum.b108zh",
        "xiaomi.vacuum.b108gl",
        "xiaomi.vacuum.d109gl",
    }
)
_SWEEP_KEYS = frozenset(
    {
        "xiaomi_back_wash_area",
        "xiaomi_carpet_avoid",
        "xiaomi_dry_time",
        "xiaomi_mop_avoid",
        "xiaomi_remember_map",
        "xiaomi_sweep_avoid",
    }
)
_CUSTOM_KEYS = frozenset({"xiaomi_precise_diagnosis", "xiaomi_water_level_remind"})
_CUSTOM_MODELS = frozenset(
    {
        "xiaomi.vacuum.ov31cn",
        "xiaomi.vacuum.ov31gl",
        "xiaomi.vacuum.ov42cn",
        "xiaomi.vacuum.ov42gl",
        "xiaomi.vacuum.pv11cn",
        "xiaomi.vacuum.pv11gl",
        "xiaomi.vacuum.pv21cn",
        "xiaomi.vacuum.pv21gl",
        "xiaomi.vacuum.qv12cn",
    }
)
_LEFT_OUT = (
    ("xiaomi.vacuum.b112", 10, 1),
    ("xiaomi.vacuum.b112bk", 10, 1),
    ("xiaomi.vacuum.b112gl", 10, 1),
    ("xiaomi.vacuum.d109gl", 20, 7),
    ("xiaomi.vacuum.d109gl", 20, 8),
)
_E10 = frozenset({"xiaomi.vacuum.b112", "xiaomi.vacuum.b112bk", "xiaomi.vacuum.b112gl"})


def _models() -> tuple[str, ...]:
    return tuple(manifest_models())


def test_approved_surface_is_eighty_five_entities() -> None:
    """The shared descriptors land on the approved models and nowhere else."""
    count = 0
    for model in _models():
        family = resolve_family(model)
        assert family is not None
        if model in _LAYOUT_MODELS:
            count += len(family.controls)
            continue
        for control in family.controls:
            if control.key in _SWEEP_KEYS or (
                control.key in _CUSTOM_KEYS and model in _CUSTOM_MODELS
            ):
                count += 1
            elif control.key in _CUSTOM_KEYS and model != "xiaomi.vacuum.ov21cn":
                raise AssertionError((model, control.key))
    assert count == 85


def test_left_out_properties_stay_unmapped() -> None:
    """The five uncertain properties stay omitted, with the plan named."""
    for model, siid, piid in _LEFT_OUT:
        family = resolve_family(model)
        assert family is not None
        assert all(
            control.siid != siid or control.piid != piid for control in family.controls
        )
        case = next(
            item
            for item in property_cases(model)
            if item.siid == siid and item.piid == piid
        )
        assert case.mapped_name is None
        assert case.omission is not None
        assert _PLAN in case.omission


def test_schedule_accepts_each_published_input(
    model: str, piid: int, value: int
) -> None:
    """A value inside an add-ii input is sent. Anything else never reaches the robot."""
    sent: list[object] = []

    class _Protocol:
        def action(self, siid: int, aiid: int, payload: object) -> dict[str, int]:
            sent.append((siid, aiid, payload))
            return {"code": 0}

    device = SimpleNamespace(
        _property_codec=SimpleNamespace(model=model),
        _protocol=_Protocol(),
    )
    fields = _fields(model, piid, value)
    if _accepted(model, piid):
        add_schedule(device, fields)
        assert sent
        payload = sent[0][2]
        assert isinstance(payload, list)
        assert {"piid": piid, "value": value} in payload
        return
    with pytest.raises(XiaomiControlException):
        add_schedule(device, fields)
    assert not sent


def test_schedule_rejects_a_step_past_each_end(
    model: str, piid: int, value: int
) -> None:
    """A value outside the spec list or range is refused before the action."""
    sent: list[object] = []

    class _Protocol:
        def action(self, siid: int, aiid: int, payload: object) -> dict[str, int]:
            del siid, aiid, payload
            sent.append(True)
            return {"code": 0}

    device = SimpleNamespace(
        _property_codec=SimpleNamespace(model=model),
        _protocol=_Protocol(),
    )
    with pytest.raises(XiaomiControlException):
        add_schedule(device, _fields(model, piid, value))
    assert not sent


def test_control_write_follows_the_spec(model: str) -> None:
    """Each new control accepts its spec values and refuses one step outside."""
    family = resolve_family(model)
    assert family is not None
    for control in family.controls:
        if control.piid is None or not control.writable:
            continue
        if (
            model not in _LAYOUT_MODELS
            and control.key not in _SWEEP_KEYS | _CUSTOM_KEYS
        ):
            continue
        spec = _spec_property(model, control.siid, control.piid)
        if spec is None:
            continue
        _assert_control_writes(model, control, spec)


def _assert_control_writes(
    model: str, control: object, spec: dict[str, object]
) -> None:
    values = spec.get("value-list")
    if isinstance(values, list) and values:
        legal = [item["value"] for item in values if isinstance(item, dict)]
        for value in legal:
            _write(model, control, value, accept=True)
        if legal:
            _write(model, control, min(legal) - 1, accept=False)
            _write(model, control, max(legal) + 1, accept=False)
        return
    bounds = spec.get("value-range")
    if isinstance(bounds, list) and len(bounds) == 3:
        start, end, step = bounds
        if isinstance(start, int) and isinstance(end, int) and isinstance(step, int):
            _write(model, control, start, accept=True)
            _write(model, control, end, accept=True)
            _write(model, control, start - step, accept=False)
            _write(model, control, end + step, accept=False)
        return
    if spec.get("format") == "bool":
        _write(model, control, True, accept=True)
        _write(model, control, False, accept=True)
        _write(model, control, 2, accept=False)


def _write(model: str, control: object, value: object, accept: bool) -> None:
    sent: list[object] = []

    class _Protocol:
        def set_property(
            self, siid: int, piid: int, raw: object
        ) -> list[dict[str, int]]:
            sent.append((siid, piid, raw))
            return [{"code": 0}]

    device = SimpleNamespace(
        _property_codec=SimpleNamespace(model=model),
        _protocol=_Protocol(),
        _xiaomi_values={},
    )
    if accept:
        write_control(device, control, value)
        assert sent
        return
    with pytest.raises(XiaomiControlException):
        write_control(device, control, value)
    assert not sent


def _fields(model: str, piid: int, value: int) -> dict[str, object]:
    fields: dict[str, object] = {
        "enable": 1,
        "day": 1,
        "hour": 1,
        "minute": 1,
        "repeat": 1,
    }
    name = {
        2: "enable",
        3: "day",
        4: "hour",
        5: "minute",
        6: "repeat",
        7: "clean_way",
        8: "suction",
        9: "water",
        10: "twice_clean",
    }[piid]
    fields[name] = value
    if model in _E10 and piid not in (7, 8, 9):
        fields.setdefault("clean_way", 0)
        fields.setdefault("suction", 0)
        fields.setdefault("water", 0)
    return fields


def _accepted(model: str, piid: int) -> bool:
    if piid == 10:
        return False
    if piid in (7, 8, 9):
        return model in _E10
    return piid in (2, 3, 4, 5, 6)


def _spec_property(
    model: str, siid: int | None, piid: int | None
) -> dict[str, object] | None:
    code = model.rsplit(".", 1)[-1]
    document = json.loads(
        Path(f"tests/xiaomi/specs/{code}.json").read_text(encoding="utf-8")
    )
    services = document.get("services")
    if not isinstance(services, list):
        return None
    for service in services:
        if not isinstance(service, dict) or service.get("iid") != siid:
            continue
        properties = service.get("properties") or []
        if not isinstance(properties, list):
            return None
        for item in properties:
            if isinstance(item, dict) and item.get("iid") == piid:
                return item
    return None


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    """Attach schedule values and control models without copying a test per model."""
    if metafunc.function.__name__ == "test_control_write_follows_the_spec":
        metafunc.parametrize("model", _models())
        return
    if metafunc.function.__name__ not in {
        "test_schedule_accepts_each_published_input",
        "test_schedule_rejects_a_step_past_each_end",
    }:
        return
    found: list[tuple[str, int, int]] = []
    for model in sorted(SCHEDULE_MODELS):
        for case in property_cases(model):
            if case.mapped_name != "xiaomi_add_schedule":
                continue
            if metafunc.function.__name__.endswith("published_input"):
                found.extend((model, case.piid, value) for value, _text in case.values)
                if case.value_range is not None:
                    start, end, _step = case.value_range
                    found.append((model, case.piid, start))
                    found.append((model, case.piid, end))
                continue
            if case.values:
                wires = [value for value, _text in case.values]
                found.append((model, case.piid, min(wires) - 1))
                found.append((model, case.piid, max(wires) + 1))
            elif case.value_range is not None:
                start, end, step = case.value_range
                found.append((model, case.piid, start - step))
                found.append((model, case.piid, end + step))
    metafunc.parametrize(("model", "piid", "value"), found)

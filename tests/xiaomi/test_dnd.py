"""The sweep disturb action is the only way to set do-not-disturb."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from custom_components.xiaomi_robot_vacuum.xiaomi.dnd import DND_MODELS, set_dnd
from custom_components.xiaomi_robot_vacuum.xiaomi.exceptions import (
    XiaomiControlException,
)
from custom_components.xiaomi_robot_vacuum.xiaomi.mapping import resolve_family
import pytest
from tests.xiaomi.deep.cases import record_of
from tests.xiaomi.deep.corpus import manifest_models

_SPECS = Path("tests/xiaomi/specs")


class _Protocol:
    def __init__(self, code: int = 0) -> None:
        self.sent: list[tuple[int, int, object]] = []
        self._code = code

    def action(self, siid: int, aiid: int, payload: object) -> dict[str, int]:
        self.sent.append((siid, aiid, payload))
        return {"code": self._code}


def _device(model: str, code: int = 0) -> tuple[SimpleNamespace, _Protocol]:
    protocol = _Protocol(code)
    device = SimpleNamespace(
        _property_codec=SimpleNamespace(model=model),
        _protocol=protocol,
    )
    return device, protocol


def _fields(**overrides: object) -> dict[str, object]:
    fields: dict[str, object] = {
        "enable": True,
        "start_hour": 22,
        "start_minute": 0,
        "end_hour": 7,
        "end_minute": 30,
    }
    fields.update(overrides)
    return fields


def test_every_disturb_action_is_in_the_dnd_models() -> None:
    """The service covers every spec that publishes set-notdisturb, and no other model."""
    found: set[str] = set()
    for model in manifest_models():
        document = json.loads((_SPECS / record_of(model).spec_file).read_text())
        for service in document["services"]:
            for action in service.get("actions") or []:
                token = (action.get("type") or "").lower()
                if "notdisturb" not in token and "disturb" not in token:
                    continue
                found.add(model)
                assert (service["iid"], action["iid"]) == (12, 1)
                assert action.get("in") == [1, 2, 3, 4, 5, 6]
                properties = {
                    prop["iid"]: prop for prop in service.get("properties") or []
                }
                assert [item["value"] for item in properties[1]["value-list"]] == [0, 1]
                assert properties[2]["value-range"][:2] == [0, 23]
                assert properties[3]["value-range"][:2] == [0, 59]
                assert properties[4]["value-range"][:2] == [0, 23]
                assert properties[5]["value-range"][:2] == [0, 59]
                assert properties[6]["value-range"][:2] == [-99999, 99999]
    assert found == set(DND_MODELS)


def test_set_dnd_sends_the_disturb_action() -> None:
    """Enable and the four clock fields go out. A missing timezone is 0."""
    device, protocol = _device("xiaomi.vacuum.b112")
    set_dnd(device, _fields())
    assert protocol.sent == [
        (
            12,
            1,
            [
                {"piid": 1, "value": 1},
                {"piid": 2, "value": 22},
                {"piid": 3, "value": 0},
                {"piid": 4, "value": 7},
                {"piid": 5, "value": 30},
                {"piid": 6, "value": 0},
            ],
        )
    ]


def test_set_dnd_sends_an_explicit_timezone() -> None:
    device, protocol = _device("xiaomi.vacuum.c101")
    set_dnd(device, _fields(enable=False, timezone=-60))
    payload = protocol.sent[0][2]
    assert {"piid": 1, "value": 0} in payload
    assert {"piid": 6, "value": -60} in payload


def test_set_dnd_rejects_a_clock_outside_the_spec() -> None:
    device, protocol = _device("xiaomi.vacuum.b112")
    with pytest.raises(XiaomiControlException):
        set_dnd(device, _fields(start_hour=24))
    with pytest.raises(XiaomiControlException):
        set_dnd(device, _fields(timezone=100_000))
    with pytest.raises(XiaomiControlException):
        set_dnd(device, _fields(extra=1))
    assert protocol.sent == []


def test_set_dnd_refuses_a_model_without_the_action() -> None:
    device, protocol = _device("xiaomi.vacuum.b108gl")
    with pytest.raises(XiaomiControlException):
        set_dnd(device, _fields())
    assert protocol.sent == []
    assert resolve_family("xiaomi.vacuum.b108gl") is not None


def test_set_dnd_rejects_a_missing_field_and_a_non_integer() -> None:
    device, protocol = _device("xiaomi.vacuum.b112")
    incomplete = _fields()
    del incomplete["end_minute"]
    with pytest.raises(XiaomiControlException):
        set_dnd(device, incomplete)
    with pytest.raises(XiaomiControlException):
        set_dnd(device, _fields(start_minute="30"))
    bare = SimpleNamespace(_protocol=protocol)
    with pytest.raises(XiaomiControlException):
        set_dnd(bare, _fields())
    assert protocol.sent == []


def test_set_dnd_raises_when_the_robot_refuses() -> None:
    device, protocol = _device("xiaomi.vacuum.d106gl", code=1)
    with pytest.raises(XiaomiControlException):
        set_dnd(device, _fields())
    assert protocol.sent

    class _Broken:
        def action(self, siid: int, aiid: int, payload: object) -> None:
            del siid, aiid, payload

    device._protocol = _Broken()
    with pytest.raises(XiaomiControlException):
        set_dnd(device, _fields())

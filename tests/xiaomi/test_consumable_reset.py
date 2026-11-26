"""Sweep consumable resets go through the published button, not a Dreame action."""

from __future__ import annotations

from types import SimpleNamespace

from custom_components.xiaomi_robot_vacuum.xiaomi.consumable import (
    reset_published_consumable,
)
from custom_components.xiaomi_robot_vacuum.xiaomi.exceptions import (
    XiaomiControlException,
)
from custom_components.xiaomi_robot_vacuum.xiaomi.mapping import resolve_family
from custom_components.xiaomi_robot_vacuum.xiaomi.schedule import SCHEDULE_MODELS
import pytest

_RESET_KEYS = {
    "main_brush": "xiaomi_reset_main_brush",
    "side_brush": "xiaomi_reset_side_brush",
    "filter": "xiaomi_reset_filter",
    "mop_pad": "xiaomi_reset_mop",
}


class _Protocol:
    def __init__(self, code: int = 0) -> None:
        self.sent: list[tuple[int, int, object]] = []
        self._code = code

    def action(self, siid: int, aiid: int, payload: object) -> dict[str, int]:
        self.sent.append((siid, aiid, payload))
        return {"code": self._code}


def test_every_schedule_model_publishes_the_four_reset_buttons() -> None:
    for model in sorted(SCHEDULE_MODELS):
        family = resolve_family(model)
        assert family is not None
        by_key = {control.key: control for control in family.controls}
        for key in _RESET_KEYS.values():
            control = by_key[key]
            assert control.siid == 7
            assert control.aiid == 1
            assert len(control.action_parameters) == 1
            piid, value = control.action_parameters[0]
            assert piid == 17
            assert isinstance(value, int) and value > 0


def test_main_brush_reset_sends_the_sweep_action() -> None:
    family = resolve_family("xiaomi.vacuum.b112")
    assert family is not None
    protocol = _Protocol()
    device = SimpleNamespace(_property_codec=family, _protocol=protocol)
    assert reset_published_consumable(device, "main_brush") is True
    assert protocol.sent == [(7, 1, [{"piid": 17, "value": 1}])]


def test_each_reset_name_sends_that_models_button() -> None:
    """Filter and mop codes differ by model. The service sends the published one."""
    for model in sorted(SCHEDULE_MODELS):
        family = resolve_family(model)
        assert family is not None
        by_key = {control.key: control for control in family.controls}
        for name, key in _RESET_KEYS.items():
            protocol = _Protocol()
            device = SimpleNamespace(_property_codec=family, _protocol=protocol)
            assert reset_published_consumable(device, name) is True
            control = by_key[key]
            expected = [
                {"piid": piid, "value": value}
                for piid, value in control.action_parameters
            ]
            assert protocol.sent == [(control.siid, control.aiid, expected)]


def test_a_station_model_keeps_the_dreame_reset() -> None:
    family = resolve_family("xiaomi.vacuum.b108gl")
    assert family is not None
    protocol = _Protocol()
    device = SimpleNamespace(_property_codec=family, _protocol=protocol)
    assert reset_published_consumable(device, "main_brush") is False
    assert reset_published_consumable(device, "detergent") is False
    assert protocol.sent == []


def test_a_device_without_controls_is_left_to_the_dreame_action() -> None:
    protocol = _Protocol()
    device = SimpleNamespace(_protocol=protocol)
    assert reset_published_consumable(device, "main_brush") is False
    assert protocol.sent == []


def test_a_refused_reset_raises() -> None:
    family = resolve_family("xiaomi.vacuum.b112")
    assert family is not None
    protocol = _Protocol(code=1)
    device = SimpleNamespace(_property_codec=family, _protocol=protocol)
    with pytest.raises(XiaomiControlException):
        reset_published_consumable(device, "filter")
    assert protocol.sent

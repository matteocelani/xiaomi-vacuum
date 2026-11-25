"""Volume is a 0..10 level on sweep specs and a 0..100 percent elsewhere."""

from __future__ import annotations

from custom_components.xiaomi_robot_vacuum.xiaomi.controls import (
    read_control,
    write_control,
)
from custom_components.xiaomi_robot_vacuum.xiaomi.exceptions import (
    XiaomiControlException,
    XiaomiValueException,
)
from custom_components.xiaomi_robot_vacuum.xiaomi.mapping import resolve_family
from tests.xiaomi.deep.cases import record_of
from tests.xiaomi.deep.corpus import manifest_models
from tests.xiaomi.spec_helpers import spec_index

_LEVEL = (0, 10, 1)
_PERCENT = (0, 100, 1)


def _volume_spec(model: str) -> tuple[int, int, tuple[int, int, int]]:
    record = record_of(model)
    current = spec_index(record.spec_file)
    for key, spec in current.items():
        kind, siid, piid = key
        if kind != "property":
            continue
        token = str(spec.get("type", "")).split(":")
        if len(token) < 4 or token[3] != "volume":
            continue
        bounds = spec.get("value-range")
        assert isinstance(bounds, list)
        return siid, piid, (bounds[0], bounds[1], bounds[2])
    raise AssertionError(model)


class _Protocol:
    def __init__(self) -> None:
        self.sent: list[tuple[int, int, int]] = []

    def set_property(self, siid: int, piid: int, value: int) -> list[dict[str, int]]:
        self.sent.append((siid, piid, value))
        return [{"code": 0}]


def test_sweep_volume_round_trips_as_a_level() -> None:
    """Wire 7 is stored and sent as 7, not as 70 and not as 7%."""
    found = 0
    for model in manifest_models():
        family = resolve_family(model)
        assert family is not None
        control = next(
            (item for item in family.controls if item.key == "xiaomi_volume"), None
        )
        if control is None:
            continue
        found += 1
        siid, piid, bounds = _volume_spec(model)
        assert (siid, piid) == (control.siid, control.piid)
        assert bounds == _LEVEL
        assert control.unit is None
        protocol = _Protocol()
        device = type("Device", (), {"_xiaomi_values": {}, "_protocol": protocol})()
        for sample in (0, 7, 10):
            write_control(device, control, sample)
            assert protocol.sent[-1] == (siid, piid, sample)
            assert read_control(device, control) == sample
        try:
            write_control(device, control, 11)
        except XiaomiControlException:
            pass
        else:
            raise AssertionError((model, "11 was sent"))
        assert protocol.sent[-1] == (siid, piid, 10)
    assert found == 10


def test_hundred_point_volume_round_trips_as_percent() -> None:
    """A 0..100 spec sends the same integer it reads, including 7 and 100."""
    found = 0
    for model in manifest_models():
        family = resolve_family(model)
        assert family is not None
        if "VOLUME" not in family.property_overrides:
            continue
        found += 1
        _siid, _piid, bounds = _volume_spec(model)
        assert bounds == _PERCENT
        assert not any(item.key == "xiaomi_volume" for item in family.controls)
        for sample in (0, 7, 70, 100):
            assert family.convert_outgoing("VOLUME", sample) == sample
            assert family.convert_incoming("VOLUME", sample) == sample
        try:
            family.convert_outgoing("VOLUME", 101)
        except XiaomiValueException:
            pass
        else:
            raise AssertionError((model, "101 was accepted"))
    missing = 0
    for model in manifest_models():
        try:
            _volume_spec(model)
        except AssertionError:
            missing += 1
    assert found == 37
    assert missing == 1

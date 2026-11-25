"""Spec units for Xiaomi controls and the Dreame sensors those models reuse."""

from __future__ import annotations

from types import SimpleNamespace

from custom_components.xiaomi_robot_vacuum.xiaomi.controls import ControlDomain
from custom_components.xiaomi_robot_vacuum.xiaomi.mapping import resolve_family
from custom_components.xiaomi_robot_vacuum.xiaomi.model import display_unit
from tests.xiaomi.deep.cases import record_of
from tests.xiaomi.deep.corpus import manifest_models
from tests.xiaomi.spec_helpers import spec_index

_SPEC_UNITS = {
    "minutes": "min",
    "hours": "h",
    "seconds": "s",
    "percentage": "%",
    "days": "d",
}
# v1 and v3 publish minutes for the same 0..18000 brush life. v2 says days.
_KEEP_MINUTES = {("mijia.vacuum.v2", "xiaomi_main_brush_minutes")}
# Spec unit is percentage, but the published range is 0..10. The entity is a level.
_VOLUME_LEVEL = "xiaomi_volume"
_DREAME_SENSOR_UNITS = {
    "CLEANING_TIME": "min",
    "DETERGENT_TIME_LEFT": "d",
    "MAIN_BRUSH_TIME_LEFT": "h",
    "SIDE_BRUSH_TIME_LEFT": "h",
    "FILTER_TIME_LEFT": "h",
    "MOP_PAD_TIME_LEFT": "h",
}


def test_control_units_follow_the_spec() -> None:
    """A numeric control shows the unit its spec publishes."""
    for model in manifest_models():
        family = resolve_family(model)
        assert family is not None
        record = record_of(model)
        current = spec_index(record.spec_file)
        for control in family.controls:
            if control.domain not in {ControlDomain.SENSOR, ControlDomain.NUMBER}:
                continue
            if control.piid is None or control.siid is None:
                continue
            spec = current[("property", control.siid, control.piid)]
            published = _SPEC_UNITS.get(spec.get("unit"))
            if published is None:
                continue
            if (model, control.key) in _KEEP_MINUTES:
                assert control.unit == "min"
                continue
            if control.key == _VOLUME_LEVEL and spec.get("value-range") == [0, 10, 1]:
                assert control.unit is None
                assert control.minimum == 0
                assert control.maximum == 10
                continue
            assert control.unit == published, (model, control.key, published)


def test_reused_dreame_sensors_use_the_spec_unit() -> None:
    """Cleaning time, detergent life, and b108 consumables are not the Dreame unit."""
    for model in manifest_models():
        family = resolve_family(model)
        assert family is not None
        device = SimpleNamespace(_property_codec=family)
        record = record_of(model)
        current = spec_index(record.spec_file)
        for name, dreame_unit in _DREAME_SENSOR_UNITS.items():
            mapping = family.property_overrides.get(name)
            if mapping is None:
                assert display_unit(device, name) is None
                continue
            spec = current.get(("property", mapping["siid"], mapping["piid"]))
            assert spec is not None
            published = _SPEC_UNITS.get(spec.get("unit"))
            shown = display_unit(device, name)
            if published is None or published == dreame_unit:
                assert shown is None, (model, name, published, shown)
                continue
            assert shown == published, (model, name, published, shown)


def test_a_dreame_device_keeps_the_default_unit() -> None:
    """Models without a Xiaomi codec do not pick up a spec override."""
    assert display_unit(SimpleNamespace(), "CLEANING_TIME") is None
    assert display_unit(SimpleNamespace(_property_codec=None), "CLEANING_TIME") is None

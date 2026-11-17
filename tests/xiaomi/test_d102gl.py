"""Spec coverage for xiaomi.vacuum.d102gl, the Xiaomi Robot Vacuum X20 Pro."""

from __future__ import annotations

from custom_components.xiaomi_robot_vacuum.xiaomi import MODEL_X20_PRO
import pytest
from tests.xiaomi.spec_helpers import (
    X20_PRO_ACTION_REASONS as _ACTION_REASONS,
    X20_PRO_PROPERTY_REASONS as _PROPERTY_REASONS,
    X20_PRO_STATE_AFTER_READ as _STATE_AFTER_READ,
    SpecCase,
    assert_controls_have_english_names,
    assert_controls_match_spec,
    assert_spec_is_fully_classified,
    exercise_control_values,
    exercise_mapped_actions,
    exercise_mapped_property_reads,
    exercise_rejected_control_traffic,
    exercise_status_wires,
    exercise_writable_values,
    mapped_addresses,
    normalize_spec,
    require_family,
    spec_index,
)

_CASE = SpecCase(
    model=MODEL_X20_PRO,
    device_name="X20 Pro",
    spec_filename="d102gl.json",
    property_reasons=_PROPERTY_REASONS,
    action_reasons=_ACTION_REASONS,
    state_after_read=_STATE_AFTER_READ,
    classification_counts={"d102gl.json": (99, 84)},
    spec_type="urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-d102gl:1",
    reason_prefix_counts={
        "identity": 5,
        "map": 46,
        "needs council": 23,
        "no ha meaning": 10,
    },
    action_spec_filenames=("d102gl.json",),
)

pytestmark = [
    pytest.mark.enable_socket,
    pytest.mark.allow_hosts(["127.0.0.1"]),
]


def test_the_published_spec_is_fully_classified() -> None:
    """Each spec item is mapped or has one explicit omission reason.

    The instances list publishes version 1 only. Version 2 is not released.
    """
    assert_spec_is_fully_classified(_CASE)


def test_every_published_status_wire_has_a_shell_state() -> None:
    """The state table covers the status value list and no extra wire."""
    listed = spec_index("d102gl.json")[("property", 2, 2)].get("value-list")
    assert isinstance(listed, list)
    wires = [item["value"] for item in listed if isinstance(item, dict)]
    family = require_family(MODEL_X20_PRO)
    assert wires == [*range(1, 22)]
    assert set(wires) == set(_STATE_AFTER_READ)
    assert set(family.state_by_wire) == set(wires)


def test_every_control_has_an_english_name() -> None:
    """Each control key and option slug has an English translation."""
    assert_controls_have_english_names(_CASE)


def test_every_mapped_property_reads_each_spec_value(socket_enabled: None) -> None:
    del socket_enabled
    exercise_mapped_property_reads(_CASE)


def test_every_writable_value_is_sent_and_unmapped_writes_are_not(
    socket_enabled: None,
) -> None:
    del socket_enabled
    exercise_writable_values(_CASE)


def test_every_mapped_action_is_invoked_or_refused_without_parameters(
    socket_enabled: None,
) -> None:
    del socket_enabled
    exercise_mapped_actions(_CASE)


def test_every_status_wire_reaches_the_shell_state(socket_enabled: None) -> None:
    del socket_enabled
    exercise_status_wires(_CASE)


def test_controls_match_the_spec() -> None:
    """Each control's options, range, and access follow the spec that defines it."""
    assert_controls_match_spec(_CASE)


def test_every_control_value_is_read_or_sent(socket_enabled: None) -> None:
    """Read every spec sample and send every writable value."""
    del socket_enabled
    exercise_control_values(_CASE)


def test_rejected_control_traffic_is_not_stored(socket_enabled: None) -> None:
    """A refused read or write leaves the stored value unchanged."""
    del socket_enabled
    exercise_rejected_control_traffic(_CASE)


def test_published_spec_matches_x20_max_except_the_known_gaps() -> None:
    """Version 1 overlaps the X20 Max spec except swing, wash area, and extras."""
    current = spec_index("d102gl.json")
    x20_max = spec_index("d109gl.json")
    assert set(current) - set(x20_max) == {
        ("property", 2, 55),
        ("property", 2, 68),
    }
    assert set(x20_max) - set(current) == {
        ("property", 2, 79),
        ("property", 2, 80),
        ("property", 2, 81),
        ("property", 2, 82),
        ("property", 2, 83),
        ("property", 2, 84),
        ("property", 20, 7),
        ("property", 20, 8),
    }
    changed = {("property", 2, 61)}
    codes = ("d102gl", "d109gl")
    for key in (set(current) & set(x20_max)) - changed:
        assert normalize_spec(current[key], codes) == normalize_spec(
            x20_max[key], codes
        ), key
    wash_area = current[("property", 2, 61)]
    assert _values(wash_area) == [0, 1, 2]
    edge = current[("property", 2, 68)]
    assert _values(edge) == [1, 2]
    assert [item.strip() for item in _descriptions(edge)] == ["Every Time", "7 Sweeps"]


def test_unpublished_station_addresses_are_not_mapped() -> None:
    """Addresses the X20 Max spec adds, and map actions, stay off the wire."""
    family = require_family(MODEL_X20_PRO)
    properties = mapped_addresses(family, "property")
    actions = mapped_addresses(family, "action")
    for pair in (
        (2, 79),
        (2, 80),
        (2, 81),
        (2, 82),
        (2, 83),
        (2, 84),
        (2, 85),
        (10, 1),
        (20, 7),
    ):
        assert pair not in properties
    for pair in ((2, 17), (2, 33), (10, 1), (16, 1)):
        assert pair not in actions
    wash = next(
        control for control in family.controls if control.key == "xiaomi_mop_wash_area"
    )
    assert [value for value, _slug in wash.options] == [0, 1, 2]
    edge = next(
        control
        for control in family.controls
        if control.key == "xiaomi_edge_sweep_frequency"
    )
    assert [(value, slug) for value, slug in edge.options] == [
        (1, "every_time"),
        (2, "seven_sweeps"),
    ]


def _values(spec: dict[str, object]) -> list[object]:
    listed = spec.get("value-list")
    assert isinstance(listed, list)
    return [item["value"] for item in listed if isinstance(item, dict)]


def _descriptions(spec: dict[str, object]) -> list[str]:
    listed = spec.get("value-list")
    assert isinstance(listed, list)
    return [str(item["description"]) for item in listed if isinstance(item, dict)]

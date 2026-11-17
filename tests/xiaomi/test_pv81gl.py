"""Spec coverage for xiaomi.vacuum.pv81gl, the Xiaomi Robot Vacuum S60."""

from __future__ import annotations

from custom_components.xiaomi_robot_vacuum.xiaomi import MODEL_S60
import pytest
from tests.xiaomi.spec_helpers import (
    S60_CLASS_ACTION_REASONS,
    S60_CLASS_PROPERTY_REASONS,
    S60_CLASS_STATE_AFTER_READ,
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
    require_family,
    spec_index,
)

_CASE = SpecCase(
    model=MODEL_S60,
    device_name="Robot Vacuum S60",
    spec_filename="pv81gl.json",
    property_reasons=S60_CLASS_PROPERTY_REASONS,
    action_reasons=S60_CLASS_ACTION_REASONS,
    state_after_read=S60_CLASS_STATE_AFTER_READ,
    classification_counts={"pv81gl.json": (78, 97)},
    spec_type="urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-pv81gl:1",
    reason_prefix_counts={
        "identity": 5,
        "map": 53,
        "needs council": 27,
        "no ha meaning": 12,
    },
    absent_items=(
        ("action", 2, 18),
        ("action", 19, 1),
        ("action", 20, 9),
        ("event", 2, 3),
        ("property", 2, 32),
        ("property", 2, 33),
        ("property", 2, 82),
        ("property", 18, 1),
        ("property", 19, 1),
        ("property", 19, 2),
        ("property", 24, 1),
    ),
    action_spec_filenames=("pv81gl.json",),
)

pytestmark = [
    pytest.mark.enable_socket,
    pytest.mark.allow_hosts(["127.0.0.1"]),
]


def test_the_published_spec_is_fully_classified() -> None:
    """Each spec item is mapped or has one explicit omission reason.

    miot-spec.org lists one released version. That version is the latest.
    """
    assert_spec_is_fully_classified(_CASE)


def test_every_published_status_wire_has_a_shell_state() -> None:
    """The state table covers the status value list and no extra wire."""
    listed = spec_index("pv81gl.json")[("property", 2, 2)].get("value-list")
    assert isinstance(listed, list)
    wires = [item["value"] for item in listed if isinstance(item, dict)]
    assert wires == [*range(1, 28)]
    assert set(wires) == set(S60_CLASS_STATE_AFTER_READ)


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
    """Read every spec sample and send every writable value, including 0 through 255."""
    del socket_enabled
    exercise_control_values(_CASE)


def test_rejected_control_traffic_is_not_stored(socket_enabled: None) -> None:
    """A refused read or write leaves the stored value unchanged."""
    del socket_enabled
    exercise_rejected_control_traffic(_CASE)


def test_charging_dock_does_not_map_the_auto_empty_station() -> None:
    """Dust-bag addresses stay off the wire. Stop-cut-hair is the only extra action."""
    family = require_family(MODEL_S60)
    properties = mapped_addresses(family, "property")
    actions = mapped_addresses(family, "action")
    assert (2, 32) not in properties
    assert (2, 33) not in properties
    assert (2, 82) not in properties
    assert (19, 1) not in properties
    assert (19, 2) not in properties
    assert (2, 18) not in actions
    assert (19, 1) not in actions
    assert (20, 9) not in actions
    assert actions[(2, 44)] == "xiaomi_stop_cut_hair"
    assert (18, 1) not in properties
    assert "CLEANING_MODE" in family.property_overrides
    assert "START_AUTO_EMPTY" not in family.action_overrides

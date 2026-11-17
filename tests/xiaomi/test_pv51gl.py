"""Spec coverage for xiaomi.vacuum.pv51gl, the Xiaomi Robot Vacuum S60+."""

from __future__ import annotations

from typing import Final

from custom_components.xiaomi_robot_vacuum.xiaomi import MODEL_S60_PLUS
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
    normalize_spec,
    require_family,
    spec_index,
)

_CASE = SpecCase(
    model=MODEL_S60_PLUS,
    device_name="Robot Vacuum S60+",
    spec_filename="pv51gl.json",
    property_reasons=S60_CLASS_PROPERTY_REASONS,
    action_reasons=S60_CLASS_ACTION_REASONS,
    state_after_read=S60_CLASS_STATE_AFTER_READ,
    classification_counts={"pv51gl.json": (85, 98)},
    spec_type="urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-pv51gl:1",
    reason_prefix_counts={
        "identity": 5,
        "map": 53,
        "needs council": 28,
        "no ha meaning": 12,
    },
    absent_items=(
        ("action", 2, 44),
        ("property", 18, 1),
        ("property", 24, 1),
    ),
    action_spec_filenames=("pv51gl.json",),
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
    listed = spec_index("pv51gl.json")[("property", 2, 2)].get("value-list")
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


def test_published_spec_matches_s60_except_the_auto_empty_dock() -> None:
    """S60+ adds the dust-bag dock. Stop-cut-hair is published only on S60."""
    current = spec_index("pv51gl.json")
    s60 = spec_index("pv81gl.json")
    assert set(current) - set(s60) == {
        ("action", 2, 18),
        ("action", 19, 1),
        ("action", 20, 9),
        ("event", 2, 3),
        ("property", 2, 32),
        ("property", 2, 33),
        ("property", 2, 82),
        ("property", 19, 1),
        ("property", 19, 2),
    }
    assert set(s60) - set(current) == {("action", 2, 44)}
    codes = ("pv51gl", "pv81gl")
    for key in set(current) & set(s60):
        assert normalize_spec(current[key], codes) == normalize_spec(s60[key], codes), (
            key
        )


def test_auto_empty_is_mapped_and_stop_cut_hair_is_not() -> None:
    """The dock empty is a mapped action. S60+'s spec does not publish stop-cut-hair."""
    family = require_family(MODEL_S60_PLUS)
    properties = mapped_addresses(family, "property")
    actions = mapped_addresses(family, "action")
    assert properties[(2, 32)] == "AUTO_DUST_COLLECTING"
    assert properties[(2, 33)] == "AUTO_EMPTY_FREQUENCY"
    assert properties[(19, 1)] == "xiaomi_dust_bag_life"
    assert actions[(2, 18)] == "START_AUTO_EMPTY"
    assert actions[(20, 9)] == "xiaomi_sweep_dust_arrest"
    assert (2, 44) not in actions
    assert (18, 1) not in properties
    assert (18, 1) not in actions


_CLEANING_MODE_WIRES: Final = (1, 2, 3, 4)


def test_cleaning_mode_publishes_mop_only() -> None:
    """The Dreame select is safe because the spec publishes mop-only as wire 2."""
    listed = spec_index("pv51gl.json")[("property", 2, 4)].get("value-list")
    assert isinstance(listed, list)
    assert [item["value"] for item in listed if isinstance(item, dict)] == list(
        _CLEANING_MODE_WIRES
    )
    assert "CLEANING_MODE" in require_family(MODEL_S60_PLUS).property_overrides

"""Spec coverage for the E10 sweep family: b112, b112gl, and b112bk."""

from __future__ import annotations

from custom_components.xiaomi_robot_vacuum.xiaomi import (
    MODEL_E10,
    MODEL_E10C,
    MODEL_E12,
)
import pytest
from tests.xiaomi.spec_helpers import (
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
    load_spec_document,
    require_family,
    spec_index,
    sweep_case,
)

_CASES = (
    sweep_case(
        MODEL_E10,
        "Robot Vacuum E10",
        "b112.json",
        "urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-b112:1",
    ),
    sweep_case(
        MODEL_E12,
        "Robot Vacuum E12",
        "b112gl.json",
        "urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-b112gl:1",
    ),
    sweep_case(
        MODEL_E10C,
        "Robot Vacuum E10C",
        "b112bk.json",
        "urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-b112bk:1",
    ),
)

pytestmark = [
    pytest.mark.enable_socket,
    pytest.mark.allow_hosts(["127.0.0.1"]),
]


@pytest.mark.parametrize("case", _CASES, ids=("b112", "b112gl", "b112bk"))
def test_the_published_spec_is_fully_classified(case: SpecCase) -> None:
    """Each released spec item is mapped or has one explicit omission reason.

    miot-spec.org lists one released version for b112 and b112gl. b112bk also
    has debug version 2, which this fixture does not use.
    """
    assert_spec_is_fully_classified(case)


@pytest.mark.parametrize("case", _CASES, ids=("b112", "b112gl", "b112bk"))
def test_every_published_status_wire_has_a_shell_state(case: SpecCase) -> None:
    """The state table covers the status value list and no extra wire."""
    listed = spec_index(case.spec_filename)[("property", 2, 1)].get("value-list")
    assert isinstance(listed, list)
    wires = [item["value"] for item in listed if isinstance(item, dict)]
    assert wires == [*range(9)]
    assert set(wires) == set(case.state_after_read)


@pytest.mark.parametrize("case", _CASES, ids=("b112", "b112gl", "b112bk"))
def test_every_control_has_an_english_name(case: SpecCase) -> None:
    """Each control key and option slug has an English translation."""
    assert_controls_have_english_names(case)


@pytest.mark.parametrize("case", _CASES, ids=("b112", "b112gl", "b112bk"))
def test_every_mapped_property_reads_each_spec_value(
    case: SpecCase, socket_enabled: None
) -> None:
    del socket_enabled
    exercise_mapped_property_reads(case)


@pytest.mark.parametrize("case", _CASES, ids=("b112", "b112gl", "b112bk"))
def test_every_writable_value_is_sent_and_unmapped_writes_are_not(
    case: SpecCase, socket_enabled: None
) -> None:
    del socket_enabled
    exercise_writable_values(case)


@pytest.mark.parametrize("case", _CASES, ids=("b112", "b112gl", "b112bk"))
def test_every_mapped_action_is_invoked_or_refused_without_parameters(
    case: SpecCase, socket_enabled: None
) -> None:
    del socket_enabled
    exercise_mapped_actions(case)


@pytest.mark.parametrize("case", _CASES, ids=("b112", "b112gl", "b112bk"))
def test_every_status_wire_reaches_the_shell_state(
    case: SpecCase, socket_enabled: None
) -> None:
    del socket_enabled
    exercise_status_wires(case)


@pytest.mark.parametrize("case", _CASES, ids=("b112", "b112gl", "b112bk"))
def test_controls_match_the_spec(case: SpecCase) -> None:
    """Each control's options, range, and access follow the spec that defines it."""
    assert_controls_match_spec(case)


@pytest.mark.parametrize("case", _CASES, ids=("b112", "b112gl", "b112bk"))
def test_every_control_value_is_read_or_sent(
    case: SpecCase, socket_enabled: None
) -> None:
    """Read every spec sample and send every writable value, including 0 through 10."""
    del socket_enabled
    exercise_control_values(case)


@pytest.mark.parametrize("case", _CASES, ids=("b112", "b112gl", "b112bk"))
def test_rejected_control_traffic_is_not_stored(
    case: SpecCase, socket_enabled: None
) -> None:
    """A refused read or write leaves the stored value unchanged."""
    del socket_enabled
    exercise_rejected_control_traffic(case)


def test_cleaning_mode_control_uses_the_published_values() -> None:
    """The Dreame select blocks sweep, so the spec values stay on a control."""
    family = require_family(MODEL_E10)
    control = next(item for item in family.controls if item.key == "xiaomi_sweep_mode")
    assert [value for value, _slug in control.options] == [0, 1, 2]
    assert "CLEANING_MODE" not in family.property_overrides


def test_e10c_uses_released_version_one_not_the_debug_spec() -> None:
    """b112bk debug version 2 is not the document this model maps."""
    document = load_spec_document("b112bk.json")
    assert document["type"] == "urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-b112bk:1"


def test_the_three_records_share_the_sweep_profile() -> None:
    """E12 and E10C declare no address diff against E10."""
    e10 = require_family(MODEL_E10)
    e12 = require_family(MODEL_E12)
    e10c = require_family(MODEL_E10C)
    assert e12.property_overrides == e10.property_overrides
    assert e10c.property_overrides == e10.property_overrides
    assert e12.action_overrides == e10.action_overrides
    assert e10c.action_overrides == e10.action_overrides
    assert e12.state_by_wire == e10.state_by_wire
    assert e10c.state_by_wire == e10.state_by_wire
    assert [control.key for control in e12.controls] == [
        control.key for control in e10.controls
    ]
    assert "RESUME" not in e10.action_overrides
    assert "PAUSE" not in e10.action_overrides
    assert "LOCATE" not in e10.action_overrides
    assert "VOLUME" not in e10.property_overrides
    assert "CHARGING_STATUS" not in e10.property_overrides
    assert "DND" not in e10.property_overrides

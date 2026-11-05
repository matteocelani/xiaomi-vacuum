"""Spec coverage for xiaomi.vacuum.ov42gl, the Xiaomi Robot Vacuum H50 Pro."""

from __future__ import annotations

from typing import Final

from custom_components.dreame_vacuum.dreame.types import DreameVacuumState
from custom_components.dreame_vacuum.xiaomi import MODEL_H50_PRO
import pytest
from tests.xiaomi.spec_helpers import (
    H50_PRO_ACTION_REASONS as _ACTION_REASONS,
    H50_PRO_PROPERTY_REASONS,
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
    normalize_spec,
    spec_index,
    with_reason_overrides,
)

_STATE_AFTER_READ: Final[dict[int, DreameVacuumState]] = {
    1: DreameVacuumState.IDLE,
    2: DreameVacuumState.CHARGING,
    3: DreameVacuumState.CHARGING,
    4: DreameVacuumState.SWEEPING,
    5: DreameVacuumState.PAUSED,
    6: DreameVacuumState.RETURNING,
    7: DreameVacuumState.RETURNING_TO_WASH,
    8: DreameVacuumState.REMOTE_CONTROL,
    9: DreameVacuumState.CHARGING_COMPLETED,
    10: DreameVacuumState.BUILDING,
    11: DreameVacuumState.UPGRADING,
    12: DreameVacuumState.STATION_CLEANING,
    13: DreameVacuumState.CHARGING,
    14: DreameVacuumState.STATION_CLEANING,
    15: DreameVacuumState.ERROR,
    16: DreameVacuumState.SWEEPING_AND_MOPPING,
    17: DreameVacuumState.MOPPING,
    18: DreameVacuumState.PAUSED,
    19: DreameVacuumState.RETURNING,
    20: DreameVacuumState.RETURNING_TO_WASH,
    21: DreameVacuumState.BUILDING,
    22: DreameVacuumState.WASHING,
    23: DreameVacuumState.CHARGING_COMPLETED,
    24: DreameVacuumState.RETURNING,
}

_CASE = SpecCase(
    model=MODEL_H50_PRO,
    device_name="H50 Pro",
    spec_filename="ov42gl.json",
    property_reasons=with_reason_overrides(
        H50_PRO_PROPERTY_REASONS,
        drop=((20, 13),),
    ),
    action_reasons=_ACTION_REASONS,
    state_after_read=_STATE_AFTER_READ,
    classification_counts={
        "ov42gl.json": (150, 111),
        "ov42gl_v1.json": (148, 109),
    },
    spec_type="urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-ov42gl:2",
    reason_prefix_counts={
        "identity": 10,
        "map": 116,
        "needs council": 71,
        "no ha meaning": 23,
    },
    version_only_controls=frozenset({(20, 13), (22, 2)}),
    absent_items=(
        ("property", 20, 9),
        ("property", 20, 11),
    ),
    action_spec_filenames=("ov42gl.json", "ov42gl_v1.json"),
    previous_spec_filename="ov42gl_v1.json",
)

pytestmark = [
    pytest.mark.enable_socket,
    pytest.mark.allow_hosts(["127.0.0.1"]),
]


def test_the_published_spec_is_fully_classified() -> None:
    """Each spec item is mapped or has one explicit omission reason.

    miot-spec.org lists released versions 1 and 2. Version 2 is the latest.
    home.miot-spec.com names xiaomi.vacuum.ov42gl the H50 Pro.
    """
    assert_spec_is_fully_classified(_CASE)


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


def test_published_spec_matches_s40_except_the_added_surface() -> None:
    """Version 2 adds H50 items and changes only the schedule-switch parameter."""
    current = spec_index("ov42gl.json")
    s40 = spec_index("ov81gl.json")
    assert set(current) - set(s40) == {
        ("action", 2, 60),
        ("event", 2, 3),
        ("event", 2, 4),
        ("event", 2, 5),
        ("event", 2, 6),
        ("event", 2, 7),
        ("event", 3, 1),
        ("event", 10, 1),
        ("event", 10, 2),
        ("event", 18, 1),
        ("property", 2, 29),
        ("property", 2, 52),
        ("property", 2, 76),
        ("property", 2, 77),
        ("property", 2, 78),
        ("property", 2, 79),
        ("property", 2, 80),
        ("property", 2, 81),
        ("property", 20, 6),
        ("property", 20, 13),
        ("property", 22, 1),
        ("property", 22, 2),
    }
    assert set(s40) - set(current) == set()
    changed = ("action", 20, 6)
    codes = ("ov42gl", "ov81gl")
    for key in (set(current) & set(s40)) - {changed}:
        assert normalize_spec(current[key], codes) == normalize_spec(s40[key], codes), (
            key
        )
    current_action = normalize_spec(current[changed], codes)
    s40_action = normalize_spec(s40[changed], codes)
    assert isinstance(current_action, dict)
    assert isinstance(s40_action, dict)
    current_fields = dict(current_action)
    s40_fields = dict(s40_action)
    assert current_fields.pop("in") == [2]
    assert s40_fields.pop("in") == [1]
    assert current_fields == s40_fields


def test_version_2_adds_only_custom_fields_and_self_check() -> None:
    """Released version 2 adds four properties that version 1 does not publish."""
    current = spec_index("ov42gl.json")
    previous = spec_index("ov42gl_v1.json")
    assert set(current) - set(previous) == {
        ("property", 20, 6),
        ("property", 20, 13),
        ("property", 22, 1),
        ("property", 22, 2),
    }
    assert set(previous) - set(current) == set()
    codes = ("xiaomi-ov42gl:1", "xiaomi-ov42gl:2")
    for key in set(previous):
        assert normalize_spec(current[key], codes) == normalize_spec(
            previous[key], codes
        ), key

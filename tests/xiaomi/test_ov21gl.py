"""Spec coverage for xiaomi.vacuum.ov21gl, the Xiaomi Robot Vacuum 5 Pro."""

from __future__ import annotations

from typing import Final

from custom_components.xiaomi_robot_vacuum.dreame.types import DreameVacuumState
from custom_components.xiaomi_robot_vacuum.xiaomi import MODEL_ROBOT_VACUUM_5_PRO
import pytest
from tests.xiaomi.spec_helpers import (
    ROBOT_VACUUM_5_PRO_ACTION_REASONS as _ACTION_REASONS,
    ROBOT_VACUUM_5_PRO_PROPERTY_REASONS as _PROPERTY_REASONS,
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
    model=MODEL_ROBOT_VACUUM_5_PRO,
    device_name="Vacuum 5 Pro",
    spec_filename="ov21gl.json",
    property_reasons=_PROPERTY_REASONS,
    action_reasons=_ACTION_REASONS,
    state_after_read=_STATE_AFTER_READ,
    classification_counts={
        "ov21gl.json": (157, 120),
        "ov21gl_v1.json": (157, 117),
    },
    spec_type="urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-ov21gl:2",
    reason_prefix_counts={
        "identity": 10,
        "map": 120,
        "needs council": 77,
        "no ha meaning": 30,
    },
    absent_items=(
        ("property", 20, 13),
        ("property", 22, 1),
        ("property", 22, 2),
    ),
    action_spec_filenames=("ov21gl.json", "ov21gl_v1.json"),
    previous_spec_filename="ov21gl_v1.json",
)

pytestmark = [
    pytest.mark.enable_socket,
    pytest.mark.allow_hosts(["127.0.0.1"]),
]


def test_the_published_spec_is_fully_classified() -> None:
    """Each spec item is mapped or has one explicit omission reason.

    miot-spec.org lists released versions 1 and 2. Version 2 is the latest.
    home.miot-spec.com names xiaomi.vacuum.ov21gl the Robot Vacuum 5 Pro.
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


def test_published_spec_matches_h50_except_stream_and_station_hardware() -> None:
    """Version 2 adds the stream service and the hardware H50 does not publish."""
    current = spec_index("ov21gl.json")
    h50 = spec_index("ov42gl.json")
    assert set(current) - set(h50) == {
        ("action", 2, 65),
        ("action", 20, 7),
        ("action", 20, 8),
        ("action", 21, 1),
        ("action", 21, 2),
        ("action", 21, 3),
        ("action", 21, 4),
        ("action", 21, 5),
        ("action", 21, 6),
        ("action", 21, 7),
        ("action", 21, 8),
        ("property", 2, 103),
        ("property", 20, 4),
        ("property", 20, 5),
        ("property", 20, 9),
        ("property", 20, 11),
        ("property", 20, 12),
        ("property", 21, 1),
        ("property", 21, 2),
        ("property", 21, 3),
        ("property", 21, 4),
        ("property", 21, 5),
        ("property", 21, 6),
        ("property", 21, 7),
        ("property", 21, 8),
    }
    assert set(h50) - set(current) == {
        ("event", 2, 6),
        ("event", 2, 7),
        ("event", 3, 1),
        ("event", 10, 1),
        ("event", 10, 2),
        ("event", 18, 1),
        ("property", 20, 13),
        ("property", 22, 1),
        ("property", 22, 2),
    }
    changed = {
        ("action", 20, 6),
        ("property", 2, 83),
        ("property", 20, 6),
    }
    codes = ("ov21gl", "ov42gl")
    for key in (set(current) & set(h50)) - changed:
        assert normalize_spec(current[key], codes) == normalize_spec(h50[key], codes), (
            key
        )
    schedule = ("action", 20, 6)
    current_action = normalize_spec(current[schedule], codes)
    h50_action = normalize_spec(h50[schedule], codes)
    assert isinstance(current_action, dict)
    assert isinstance(h50_action, dict)
    current_fields = dict(current_action)
    h50_fields = dict(h50_action)
    assert current_fields.pop("in") == [1]
    assert h50_fields.pop("in") == [2]
    assert current_fields == h50_fields
    listed = current[("property", 2, 83)].get("value-list")
    assert isinstance(listed, list)
    assert [item["description"] for item in listed if isinstance(item, dict)] == [
        "Silent",
        "Deep Clean",
        "Standard",
        "Butler",
        "Pet ",
    ]
    current_access = current[("property", 20, 6)].get("access")
    h50_access = h50[("property", 20, 6)].get("access")
    assert isinstance(current_access, list)
    assert isinstance(h50_access, list)
    assert sorted(current_access) == sorted(h50_access) == ["notify", "read", "write"]


def test_s40_spec_is_a_subset_aside_from_worry_free_labels() -> None:
    """Every S40 item is in this spec, and only worry-free labels differ."""
    current = spec_index("ov21gl.json")
    s40 = spec_index("ov81gl.json")
    assert set(s40) <= set(current)
    changed = {("property", 2, 83)}
    codes = ("ov21gl", "ov81gl")
    for key in set(s40) - changed:
        assert normalize_spec(current[key], codes) == normalize_spec(s40[key], codes), (
            key
        )


def test_version_2_adds_map_rotate_patrol_and_hidden_zone() -> None:
    """Released version 2 adds three items that version 1 does not publish."""
    current = spec_index("ov21gl.json")
    previous = spec_index("ov21gl_v1.json")
    assert set(current) - set(previous) == {
        ("action", 2, 65),
        ("action", 20, 8),
        ("property", 2, 103),
    }
    assert set(previous) - set(current) == set()
    codes = ("xiaomi-ov21gl:1", "xiaomi-ov21gl:2")
    for key in set(previous):
        assert normalize_spec(current[key], codes) == normalize_spec(
            previous[key], codes
        ), key

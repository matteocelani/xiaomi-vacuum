"""Spec coverage for xiaomi.vacuum.pv11gl, the Xiaomi Robot Vacuum 6 Max."""

from __future__ import annotations

from custom_components.dreame_vacuum.xiaomi import MODEL_ROBOT_VACUUM_6_MAX
import pytest
from tests.xiaomi.spec_helpers import (
    VACUUM_6_MAX_ACTION_REASONS as _ACTION_REASONS,
    VACUUM_6_MAX_PROPERTY_REASONS as _PROPERTY_REASONS,
    VACUUM_6_MAX_STATE_AFTER_READ as _STATE_AFTER_READ,
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
    model=MODEL_ROBOT_VACUUM_6_MAX,
    device_name="Robot Vacuum 6 Max",
    spec_filename="pv11gl.json",
    property_reasons=_PROPERTY_REASONS,
    action_reasons=_ACTION_REASONS,
    state_after_read=_STATE_AFTER_READ,
    classification_counts={"pv11gl.json": (152, 123)},
    spec_type="urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-pv11gl:1",
    reason_prefix_counts={
        "identity": 5,
        "map": 59,
        "needs council": 43,
        "no ha meaning": 16,
    },
    absent_items=(
        ("action", 2, 66),
        ("action", 20, 16),
        ("property", 2, 104),
        ("property", 2, 105),
        ("property", 2, 106),
        ("property", 23, 1),
        ("property", 23, 2),
        ("property", 23, 3),
    ),
    action_spec_filenames=("pv11gl.json",),
)

pytestmark = [
    pytest.mark.enable_socket,
    pytest.mark.allow_hosts(["127.0.0.1"]),
]


def test_the_published_spec_is_fully_classified() -> None:
    """Each spec item is mapped or has one explicit omission reason.

    home.miot-spec.com lists released version 1 only. miot-spec.org's released
    instance list matches. Xiaomi's compliance list names this model PV11GL.
    """
    assert_spec_is_fully_classified(_CASE)


def test_every_published_status_wire_has_a_shell_state() -> None:
    """The state table covers the status value list and no extra wire."""
    listed = spec_index("pv11gl.json")[("property", 2, 2)].get("value-list")
    assert isinstance(listed, list)
    wires = [item["value"] for item in listed if isinstance(item, dict)]
    assert wires == [*range(1, 22), 24, 25, 26, 27]
    assert set(wires) == set(_STATE_AFTER_READ)


def test_video_password_actions_are_not_mapped() -> None:
    """Password actions stay off the wire. There is no confirmation flow."""
    actions = mapped_addresses(require_family(MODEL_ROBOT_VACUUM_6_MAX), "action")
    assert (21, 6) not in actions
    assert (21, 7) not in actions
    assert (21, 8) not in actions


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


def test_published_spec_matches_robot_vacuum_6_except_station_hardware() -> None:
    """Version 1 adds mop, detergent, camera, and stream items Robot Vacuum 6 lacks."""
    current = spec_index("pv11gl.json")
    vacuum_6 = spec_index("pv32gl.json")
    assert set(current) - set(vacuum_6) == {
        ("action", 2, 19),
        ("action", 2, 21),
        ("action", 2, 22),
        ("action", 9, 1),
        ("action", 18, 1),
        ("action", 20, 7),
        ("action", 20, 8),
        ("action", 20, 11),
        ("action", 20, 12),
        ("action", 20, 13),
        ("action", 20, 14),
        ("action", 20, 15),
        ("action", 21, 4),
        ("action", 21, 5),
        ("action", 21, 6),
        ("action", 21, 7),
        ("action", 21, 8),
        ("property", 2, 44),
        ("property", 2, 46),
        ("property", 2, 47),
        ("property", 2, 48),
        ("property", 2, 59),
        ("property", 2, 60),
        ("property", 2, 71),
        ("property", 2, 76),
        ("property", 2, 78),
        ("property", 2, 92),
        ("property", 2, 93),
        ("property", 2, 94),
        ("property", 2, 95),
        ("property", 2, 97),
        ("property", 2, 98),
        ("property", 2, 107),
        ("property", 9, 1),
        ("property", 9, 2),
        ("property", 18, 1),
        ("property", 18, 2),
        ("property", 18, 3),
        ("property", 18, 4),
        ("property", 20, 9),
        ("property", 20, 10),
        ("property", 20, 11),
        ("property", 20, 12),
        ("property", 20, 13),
        ("property", 20, 14),
        ("property", 20, 15),
        ("property", 21, 2),
        ("property", 21, 4),
        ("property", 21, 5),
        ("property", 21, 6),
        ("property", 21, 7),
        ("property", 21, 8),
    }
    assert set(vacuum_6) - set(current) == {
        ("action", 2, 66),
        ("action", 20, 16),
        ("property", 2, 104),
        ("property", 2, 105),
        ("property", 2, 106),
        ("property", 23, 1),
        ("property", 23, 2),
        ("property", 23, 3),
    }
    changed = {
        ("property", 2, 2),
        ("property", 2, 61),
    }
    type_only = {
        ("action", 20, 9),
        ("action", 20, 10),
        ("property", 13, 1),
        ("property", 14, 1),
        ("property", 14, 2),
    }
    codes = ("pv11gl", "pv32gl")
    for key in (set(current) & set(vacuum_6)) - changed - type_only:
        assert normalize_spec(current[key], codes) == normalize_spec(
            vacuum_6[key], codes
        ), key
    for key in type_only:
        left = normalize_spec(current[key], codes)
        right = normalize_spec(vacuum_6[key], codes)
        assert isinstance(left, dict)
        assert isinstance(right, dict)
        left_fields = dict(left)
        right_fields = dict(right)
        left_type = left_fields.pop("type")
        right_type = right_fields.pop("type")
        left_fields.pop("gatt-access", None)
        right_fields.pop("gatt-access", None)
        assert left_fields == right_fields
        assert (
            str(left_type).split(":xiaomi-")[0] == str(right_type).split(":xiaomi-")[0]
        )
    status = current[("property", 2, 2)].get("value-list")
    assert isinstance(status, list)
    assert [item["value"] for item in status if isinstance(item, dict)] == [
        *range(1, 22),
        24,
        25,
        26,
        27,
    ]
    area = current[("property", 2, 61)]
    other_area = vacuum_6[("property", 2, 61)]
    assert _values(area) == _values(other_area)
    assert [item.replace("  ", " ") for item in _descriptions(area)] == _descriptions(
        other_area
    )


def _values(spec: dict[str, object]) -> list[object]:
    listed = spec.get("value-list")
    assert isinstance(listed, list)
    return [item["value"] for item in listed if isinstance(item, dict)]


def _descriptions(spec: dict[str, object]) -> list[str]:
    listed = spec.get("value-list")
    assert isinstance(listed, list)
    return [str(item["description"]) for item in listed if isinstance(item, dict)]

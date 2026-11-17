"""Spec coverage for xiaomi.vacuum.pv32gl, the Xiaomi Robot Vacuum 6."""

from __future__ import annotations

from typing import Final

from custom_components.xiaomi_robot_vacuum.dreame.types import DreameVacuumState
from custom_components.xiaomi_robot_vacuum.xiaomi import MODEL_ROBOT_VACUUM_6
import pytest
from tests.xiaomi.spec_helpers import (
    ROBOT_VACUUM_6_ACTION_REASONS as _ACTION_REASONS,
    ROBOT_VACUUM_6_PROPERTY_REASONS as _PROPERTY_REASONS,
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
    24: DreameVacuumState.RETURNING,
}

_CASE = SpecCase(
    model=MODEL_ROBOT_VACUUM_6,
    device_name="Robot Vacuum 6",
    spec_filename="pv32gl.json",
    property_reasons=_PROPERTY_REASONS,
    action_reasons=_ACTION_REASONS,
    state_after_read=_STATE_AFTER_READ,
    classification_counts={
        "pv32gl.json": (115, 116),
        "pv32gl_v1.json": (115, 115),
    },
    spec_type="urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-pv32gl:2",
    reason_prefix_counts={
        "identity": 10,
        "map": 124,
        "needs council": 67,
        "no ha meaning": 30,
    },
    absent_items=(
        ("action", 2, 5),
        ("action", 2, 19),
        ("action", 9, 1),
        ("action", 16, 1),
        ("action", 18, 1),
        ("action", 20, 7),
        ("action", 21, 3),
        ("property", 2, 52),
        ("property", 9, 1),
        ("property", 9, 2),
        ("property", 18, 1),
        ("property", 18, 4),
        ("property", 20, 9),
        ("property", 20, 11),
        ("property", 21, 2),
    ),
    action_spec_filenames=("pv32gl.json", "pv32gl_v1.json"),
    previous_spec_filename="pv32gl_v1.json",
)

pytestmark = [
    pytest.mark.enable_socket,
    pytest.mark.allow_hosts(["127.0.0.1"]),
]


def test_the_published_spec_is_fully_classified() -> None:
    """Each spec item is mapped or has one explicit omission reason.

    miot-spec.org lists released versions 1 and 2. Version 2 is the latest.
    home.miot-spec.com names xiaomi.vacuum.pv32gl the Xiaomi Robot Vacuum 6.
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


def test_published_spec_matches_vacuum_5_pro_except_roller_and_hardware() -> None:
    """Version 2 replaces the 5 Pro lidar and mop-pad hardware with a roller."""
    current = spec_index("pv32gl.json")
    vacuum_5_pro = spec_index("ov21gl.json")
    assert set(current) - set(vacuum_5_pro) == {
        ("action", 2, 66),
        ("action", 20, 4),
        ("action", 20, 9),
        ("action", 20, 10),
        ("action", 20, 16),
        ("action", 24, 1),
        ("action", 24, 2),
        ("action", 24, 3),
        ("property", 2, 104),
        ("property", 2, 105),
        ("property", 2, 106),
        ("property", 22, 1),
        ("property", 22, 2),
        ("property", 23, 1),
        ("property", 23, 2),
        ("property", 23, 3),
        ("property", 24, 1),
        ("property", 24, 2),
        ("property", 24, 3),
        ("property", 24, 4),
    }
    assert set(vacuum_5_pro) - set(current) == {
        ("action", 2, 5),
        ("action", 2, 19),
        ("action", 2, 21),
        ("action", 2, 22),
        ("action", 2, 43),
        ("action", 2, 44),
        ("action", 2, 63),
        ("action", 2, 64),
        ("action", 9, 1),
        ("action", 16, 1),
        ("action", 17, 1),
        ("action", 18, 1),
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
        ("property", 2, 37),
        ("property", 2, 44),
        ("property", 2, 46),
        ("property", 2, 47),
        ("property", 2, 48),
        ("property", 2, 49),
        ("property", 2, 50),
        ("property", 2, 51),
        ("property", 2, 52),
        ("property", 2, 55),
        ("property", 2, 59),
        ("property", 2, 60),
        ("property", 2, 63),
        ("property", 2, 64),
        ("property", 2, 69),
        ("property", 2, 71),
        ("property", 2, 76),
        ("property", 2, 78),
        ("property", 2, 82),
        ("property", 2, 92),
        ("property", 2, 93),
        ("property", 2, 94),
        ("property", 2, 95),
        ("property", 2, 97),
        ("property", 2, 98),
        ("property", 9, 1),
        ("property", 9, 2),
        ("property", 17, 1),
        ("property", 17, 2),
        ("property", 18, 1),
        ("property", 18, 2),
        ("property", 18, 3),
        ("property", 18, 4),
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
    changed = {
        ("action", 2, 65),
        ("property", 2, 2),
        ("property", 2, 4),
        ("property", 2, 61),
        ("property", 2, 83),
        ("property", 2, 101),
        ("property", 2, 103),
        ("property", 13, 1),
        ("property", 14, 1),
        ("property", 14, 2),
    }
    codes = ("pv32gl", "ov21gl")
    for key in (set(current) & set(vacuum_5_pro)) - changed:
        assert normalize_spec(current[key], codes) == normalize_spec(
            vacuum_5_pro[key], codes
        ), key
    _assert_value_lists(current, vacuum_5_pro, codes)


def test_published_spec_matches_h50_except_roller_and_stream() -> None:
    """Version 2 drops the H50 stream and mop-pad services and adds the roller."""
    current = spec_index("pv32gl.json")
    h50 = spec_index("ov43gb.json")
    assert set(current) - set(h50) == {
        ("action", 2, 65),
        ("action", 2, 66),
        ("action", 20, 4),
        ("action", 20, 9),
        ("action", 20, 10),
        ("action", 20, 16),
        ("action", 24, 1),
        ("action", 24, 2),
        ("action", 24, 3),
        ("property", 2, 103),
        ("property", 2, 104),
        ("property", 2, 105),
        ("property", 2, 106),
        ("property", 20, 4),
        ("property", 20, 5),
        ("property", 20, 6),
        ("property", 23, 1),
        ("property", 23, 2),
        ("property", 23, 3),
        ("property", 24, 1),
        ("property", 24, 2),
        ("property", 24, 3),
        ("property", 24, 4),
    }
    assert set(h50) - set(current) == {
        ("action", 2, 5),
        ("action", 2, 19),
        ("action", 2, 21),
        ("action", 2, 22),
        ("action", 2, 43),
        ("action", 2, 44),
        ("action", 2, 63),
        ("action", 2, 64),
        ("action", 9, 1),
        ("action", 16, 1),
        ("action", 17, 1),
        ("action", 18, 1),
        ("action", 21, 1),
        ("action", 21, 2),
        ("action", 21, 3),
        ("action", 21, 5),
        ("action", 21, 6),
        ("action", 21, 7),
        ("action", 21, 8),
        ("event", 2, 6),
        ("event", 2, 7),
        ("event", 3, 1),
        ("event", 10, 1),
        ("event", 10, 2),
        ("event", 18, 1),
        ("property", 2, 37),
        ("property", 2, 44),
        ("property", 2, 46),
        ("property", 2, 47),
        ("property", 2, 48),
        ("property", 2, 49),
        ("property", 2, 50),
        ("property", 2, 51),
        ("property", 2, 52),
        ("property", 2, 55),
        ("property", 2, 59),
        ("property", 2, 60),
        ("property", 2, 63),
        ("property", 2, 64),
        ("property", 2, 69),
        ("property", 2, 71),
        ("property", 2, 76),
        ("property", 2, 78),
        ("property", 2, 82),
        ("property", 2, 92),
        ("property", 2, 93),
        ("property", 2, 94),
        ("property", 2, 95),
        ("property", 2, 97),
        ("property", 2, 98),
        ("property", 9, 1),
        ("property", 9, 2),
        ("property", 17, 1),
        ("property", 17, 2),
        ("property", 18, 1),
        ("property", 18, 2),
        ("property", 18, 3),
        ("property", 18, 4),
        ("property", 21, 1),
        ("property", 21, 2),
        ("property", 21, 3),
        ("property", 21, 4),
        ("property", 21, 5),
        ("property", 21, 6),
        ("property", 21, 7),
        ("property", 21, 8),
    }
    changed = {
        ("property", 2, 2),
        ("property", 2, 4),
        ("property", 2, 31),
        ("property", 2, 61),
        ("property", 2, 83),
        ("property", 2, 101),
        ("property", 13, 1),
        ("property", 14, 1),
        ("property", 14, 2),
        ("property", 22, 1),
        ("property", 22, 2),
    }
    codes = ("pv32gl", "ov43gb")
    for key in (set(current) & set(h50)) - changed:
        assert normalize_spec(current[key], codes) == normalize_spec(h50[key], codes), (
            key
        )
    _assert_value_lists(current, h50, codes)
    drying = current[("property", 2, 31)].get("value-list")
    assert isinstance(drying, list)
    assert [item["description"] for item in drying if isinstance(item, dict)] == [
        "2 Hours",
        "3 Hours",
        "4 Hours",
    ]


def test_version_2_adds_only_ota_info() -> None:
    """Released version 2 adds the OTA-info action and leaves every other item."""
    current = spec_index("pv32gl.json")
    previous = spec_index("pv32gl_v1.json")
    assert set(current) - set(previous) == {("action", 20, 16)}
    assert set(previous) - set(current) == set()
    codes = ("xiaomi-pv32gl:1", "xiaomi-pv32gl:2")
    for key in set(previous):
        assert normalize_spec(current[key], codes) == normalize_spec(
            previous[key], codes
        ), key


def _assert_value_lists(
    current: dict[tuple[str, int, int], dict[str, object]],
    other: dict[tuple[str, int, int], dict[str, object]],
    codes: tuple[str, ...],
) -> None:
    """Assert the status, mode, and tank lists that differ from a neighbor."""
    status = current[("property", 2, 2)].get("value-list")
    assert isinstance(status, list)
    assert [item["value"] for item in status if isinstance(item, dict)] == [
        *range(1, 22),
        24,
    ]
    mode = current[("property", 2, 4)].get("value-list")
    assert isinstance(mode, list)
    assert [item["value"] for item in mode if isinstance(item, dict)] == [1, 3, 4]
    assert [item["description"] for item in mode if isinstance(item, dict)] == [
        "Sweep",
        "Sweep Mop",
        "Sweep Before Mopping",
    ]
    worry_free = current[("property", 2, 83)].get("value-list")
    assert isinstance(worry_free, list)
    assert [item["description"] for item in worry_free if isinstance(item, dict)] == [
        "Silent Clean",
        "Deep Clean",
        "General",
        "Butler",
    ]
    tank = current[("property", 2, 101)].get("value-list")
    assert isinstance(tank, list)
    assert [item["description"] for item in tank if isinstance(item, dict)] == [
        "Idle",
        "Empting",
        "Empting Completed",
        "Empting Failed",
        "Not Installed",
    ]
    area = current[("property", 2, 61)]
    other_area = other[("property", 2, 61)]
    assert _values(area) == _values(other_area)
    assert _descriptions(area) != _descriptions(other_area)
    assert [item.replace("  ", " ") for item in _descriptions(other_area)] == (
        _descriptions(area)
    )
    for key in (
        ("action", 2, 65),
        ("property", 2, 103),
        ("property", 13, 1),
        ("property", 14, 1),
        ("property", 14, 2),
    ):
        if key not in other:
            continue
        left = normalize_spec(current[key], codes)
        right = normalize_spec(other[key], codes)
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


def _values(spec: dict[str, object]) -> list[object]:
    listed = spec.get("value-list")
    assert isinstance(listed, list)
    return [item["value"] for item in listed if isinstance(item, dict)]


def _descriptions(spec: dict[str, object]) -> list[str]:
    listed = spec.get("value-list")
    assert isinstance(listed, list)
    return [str(item["description"]) for item in listed if isinstance(item, dict)]

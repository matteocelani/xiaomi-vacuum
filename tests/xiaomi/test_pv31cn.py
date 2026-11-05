"""Spec coverage for xiaomi.vacuum.pv31cn, the Mijia Robot Vacuum 5."""

from __future__ import annotations

from typing import Final

from custom_components.dreame_vacuum.dreame.types import DreameVacuumState
from custom_components.dreame_vacuum.xiaomi import (
    MODEL_H50_PRO,
    MODEL_MIJIA_ROBOT_VACUUM_5,
)
import pytest
from tests.xiaomi.spec_helpers import (
    H50_PRO_ACTION_REASONS,
    H50_PRO_PROPERTY_REASONS,
    ROBOT_VACUUM_6_ACTION_REASONS,
    ROBOT_VACUUM_6_PROPERTY_REASONS,
    S60_CLASS_ACTION_REASONS,
    S60_CLASS_PROPERTY_REASONS,
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
    require_family,
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
    model=MODEL_MIJIA_ROBOT_VACUUM_5,
    device_name="Mijia Robot Vacuum 5",
    spec_filename="pv31cn.json",
    property_reasons=with_reason_overrides(
        H50_PRO_PROPERTY_REASONS,
        drop=((20, 13),),
        add={
            (2, 103): S60_CLASS_PROPERTY_REASONS[(2, 103)],
            (2, 104): ROBOT_VACUUM_6_PROPERTY_REASONS[(2, 104)],
            (2, 105): ROBOT_VACUUM_6_PROPERTY_REASONS[(2, 105)],
            (2, 106): S60_CLASS_PROPERTY_REASONS[(2, 106)],
            (20, 4): ROBOT_VACUUM_6_PROPERTY_REASONS[(20, 4)],
            (20, 5): ROBOT_VACUUM_6_PROPERTY_REASONS[(20, 5)],
            (23, 1): ROBOT_VACUUM_6_PROPERTY_REASONS[(23, 1)],
            (23, 2): ROBOT_VACUUM_6_PROPERTY_REASONS[(23, 2)],
            (23, 3): ROBOT_VACUUM_6_PROPERTY_REASONS[(23, 3)],
        },
    ),
    action_reasons=with_reason_overrides(
        H50_PRO_ACTION_REASONS,
        add={
            (2, 65): S60_CLASS_ACTION_REASONS[(2, 65)],
            (2, 66): ROBOT_VACUUM_6_ACTION_REASONS[(2, 66)],
            (20, 4): ROBOT_VACUUM_6_ACTION_REASONS[(20, 4)],
        },
    ),
    state_after_read=_STATE_AFTER_READ,
    classification_counts={"pv31cn.json": (148, 117)},
    spec_type="urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-pv31cn:1",
    reason_prefix_counts={
        "identity": 5,
        "map": 63,
        "needs council": 34,
        "no ha meaning": 15,
    },
    absent_items=(
        ("action", 2, 22),
        ("property", 20, 13),
    ),
    action_spec_filenames=("pv31cn.json",),
)

pytestmark = [
    pytest.mark.enable_socket,
    pytest.mark.allow_hosts(["127.0.0.1"]),
]


def test_the_published_spec_is_fully_classified() -> None:
    """Each spec item is mapped or has one explicit omission reason.

    miot-spec.org lists one released version. That version is the latest.
    There is no preview.
    """
    assert_spec_is_fully_classified(_CASE)


def test_every_published_status_wire_has_a_shell_state() -> None:
    """The state table covers the status value list and no extra wire."""
    listed = spec_index("pv31cn.json")[("property", 2, 2)].get("value-list")
    assert isinstance(listed, list)
    wires = [item["value"] for item in listed if isinstance(item, dict)]
    assert set(wires) == set(_STATE_AFTER_READ)


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


def test_call_clean_and_the_host_tank_are_the_only_record_diff() -> None:
    """H50 Pro stays unchanged. This model drops call-clean and adds Not Installed."""
    current = require_family(MODEL_MIJIA_ROBOT_VACUUM_5)
    base = require_family(MODEL_H50_PRO)
    assert current.property_overrides == base.property_overrides
    assert current.action_overrides == base.action_overrides
    assert current.state_by_wire == base.state_by_wire
    assert current.task_by_wire == base.task_by_wire
    dropped = {control.key for control in base.controls} - {
        control.key for control in current.controls
    }
    assert dropped == {"xiaomi_call_clean", "xiaomi_water_level_remind"}
    current_tank = next(
        control.options
        for control in current.controls
        if control.key == "xiaomi_host_tank"
    )
    base_tank = next(
        control.options
        for control in base.controls
        if control.key == "xiaomi_host_tank"
    )
    assert [value for value, _slug in current_tank] == [0, 1, 2, 3, 4]
    assert [value for value, _slug in base_tank] == [0, 1, 2, 3]
    assert "xiaomi_call_clean" in {control.key for control in base.controls}

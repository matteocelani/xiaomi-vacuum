"""Spec coverage for xiaomi.vacuum.qv41cn, the Mijia 7C."""

from __future__ import annotations

from typing import Final

from custom_components.xiaomi_robot_vacuum.dreame.types import DreameVacuumState
from custom_components.xiaomi_robot_vacuum.xiaomi import (
    MODEL_H50_PRO_ROLLER,
    MODEL_MIJIA_7C,
)
import pytest
from tests.xiaomi.spec_helpers import (
    ROBOT_VACUUM_6_ACTION_REASONS,
    ROBOT_VACUUM_6_PROPERTY_REASONS,
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
    24: DreameVacuumState.RETURNING,
}

_CASE = SpecCase(
    model=MODEL_MIJIA_7C,
    device_name="Mijia 7C",
    spec_filename="qv41cn.json",
    property_reasons=with_reason_overrides(ROBOT_VACUUM_6_PROPERTY_REASONS),
    action_reasons=with_reason_overrides(
        ROBOT_VACUUM_6_ACTION_REASONS,
        drop=((20, 16),),
    ),
    state_after_read=_STATE_AFTER_READ,
    classification_counts={"qv41cn.json": (115, 116)},
    spec_type="urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-qv41cn:1",
    reason_prefix_counts={
        "identity": 5,
        "map": 62,
        "needs council": 34,
        "no ha meaning": 15,
    },
    absent_items=(
        ("action", 2, 5),
        ("action", 9, 1),
        ("action", 18, 1),
        ("action", 20, 16),
        ("property", 2, 79),
        ("property", 2, 84),
        ("property", 2, 91),
        ("property", 9, 1),
        ("property", 18, 1),
    ),
    action_spec_filenames=("qv41cn.json",),
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
    listed = spec_index("qv41cn.json")[("property", 2, 2)].get("value-list")
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


def test_the_chinese_spec_drops_wash_temperature_and_ota_info() -> None:
    """Those two items stay off this model. The global record is not edited."""
    current = spec_index("qv41cn.json")
    global_spec = spec_index("qv41gl.json")
    assert set(current) - set(global_spec) == {("event", 2, 6)}
    assert set(global_spec) - set(current) == {
        ("action", 20, 16),
        ("property", 2, 84),
    }
    chinese = require_family(MODEL_MIJIA_7C)
    global_model = require_family(MODEL_H50_PRO_ROLLER)
    assert chinese.property_overrides == global_model.property_overrides
    assert chinese.action_overrides == global_model.action_overrides
    assert chinese.state_by_wire == global_model.state_by_wire
    dropped = {control.key for control in global_model.controls} - {
        control.key for control in chinese.controls
    }
    assert dropped == {"xiaomi_wash_water_temperature"}
    assert "xiaomi_wash_water_temperature" in {
        control.key for control in global_model.controls
    }

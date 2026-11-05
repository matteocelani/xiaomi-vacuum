"""Spec coverage for xiaomi.vacuum.ov31cn, the Mijia M40 S."""

from __future__ import annotations

from typing import Final

from custom_components.dreame_vacuum.dreame.types import DreameVacuumState
from custom_components.dreame_vacuum.xiaomi.mapping import (
    MODEL_MIJIA_M40_S,
    MODEL_ROBOT_VACUUM_5,
)
import pytest
from tests.xiaomi.spec_helpers import (
    ROBOT_VACUUM_5_ACTION_REASONS,
    ROBOT_VACUUM_5_PROPERTY_REASONS,
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
_SELF_CHECK_ITEMS: Final = (
    "no ha meaning: self-check items are neither readable nor writable."
)

_CASE = SpecCase(
    model=MODEL_MIJIA_M40_S,
    device_name="Mijia M40 S",
    spec_filename="ov31cn.json",
    property_reasons=with_reason_overrides(
        ROBOT_VACUUM_5_PROPERTY_REASONS,
        add={(22, 1): _SELF_CHECK_ITEMS},
    ),
    action_reasons=with_reason_overrides(ROBOT_VACUUM_5_ACTION_REASONS),
    state_after_read=_STATE_AFTER_READ,
    classification_counts={
        "ov31cn.json": (134, 103),
        "ov31cn_v1.json": (130, 100),
    },
    spec_type="urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-ov31cn:2",
    reason_prefix_counts={
        "identity": 10,
        "map": 108,
        "needs council": 61,
        "no ha meaning": 24,
    },
    version_only_controls=frozenset({(20, 9), (20, 10), (20, 11), (22, 2)}),
    action_spec_filenames=("ov31cn.json", "ov31cn_v1.json"),
    previous_spec_filename="ov31cn_v1.json",
)

pytestmark = [
    pytest.mark.enable_socket,
    pytest.mark.allow_hosts(["127.0.0.1"]),
]


def test_the_published_spec_is_fully_classified() -> None:
    """Each spec item is mapped or has one explicit omission reason.

    miot-spec.org lists released versions 1 and 2. Version 2 is the latest.
    """
    assert_spec_is_fully_classified(_CASE)


def test_every_published_status_wire_has_a_shell_state() -> None:
    """The state table covers the status value list and no extra wire."""
    listed = spec_index("ov31cn.json")[("property", 2, 2)].get("value-list")
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


def test_version_2_adds_self_check_and_keeps_the_global_record() -> None:
    """The result string is mapped. Items with no access stay omitted."""
    current = spec_index("ov31cn.json")
    global_spec = spec_index("ov31gl.json")
    assert set(current) - set(global_spec) == {("property", 22, 1), ("property", 22, 2)}
    assert set(global_spec) - set(current) == set()
    chinese = require_family(MODEL_MIJIA_M40_S)
    global_model = require_family(MODEL_ROBOT_VACUUM_5)
    assert chinese.property_overrides == global_model.property_overrides
    assert chinese.action_overrides == global_model.action_overrides
    assert chinese.state_by_wire == global_model.state_by_wire
    added = {control.key for control in chinese.controls} - {
        control.key for control in global_model.controls
    }
    assert added == {"xiaomi_self_check_results"}
    assert "xiaomi_self_check_results" not in {
        control.key for control in global_model.controls
    }

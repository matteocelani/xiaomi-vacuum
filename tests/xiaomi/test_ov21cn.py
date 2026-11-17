"""Spec coverage for xiaomi.vacuum.ov21cn, the Mijia 5 Pro."""

from __future__ import annotations

from typing import Final

from custom_components.xiaomi_robot_vacuum.dreame.types import DreameVacuumState
from custom_components.xiaomi_robot_vacuum.xiaomi import (
    MODEL_MIJIA_5_PRO,
    MODEL_ROBOT_VACUUM_5_PRO,
)
import pytest
from tests.xiaomi.spec_helpers import (
    ROBOT_VACUUM_5_PRO_ACTION_REASONS,
    ROBOT_VACUUM_5_PRO_PROPERTY_REASONS,
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
_XIAOAI_BIND: Final = (
    "no ha meaning: the Xiaoai bind id is a diagnostic fetch, not a user control."
)

_CASE = SpecCase(
    model=MODEL_MIJIA_5_PRO,
    device_name="Mijia 5 Pro",
    spec_filename="ov21cn.json",
    property_reasons=with_reason_overrides(
        ROBOT_VACUUM_5_PRO_PROPERTY_REASONS,
        add={(22, 1): _SELF_CHECK_ITEMS},
    ),
    action_reasons=with_reason_overrides(
        ROBOT_VACUUM_5_PRO_ACTION_REASONS,
        add={(20, 4): _XIAOAI_BIND},
    ),
    state_after_read=_STATE_AFTER_READ,
    classification_counts={
        "ov21cn.json": (159, 122),
        "ov21cn_v1.json": (159, 119),
    },
    spec_type="urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-ov21cn:2",
    reason_prefix_counts={
        "identity": 10,
        "map": 120,
        "needs council": 77,
        "no ha meaning": 34,
    },
    absent_items=(("property", 20, 13),),
    action_spec_filenames=("ov21cn.json", "ov21cn_v1.json"),
    previous_spec_filename="ov21cn_v1.json",
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
    listed = spec_index("ov21cn.json")[("property", 2, 2)].get("value-list")
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


def test_value_lists_and_added_items_do_not_change_the_global_record() -> None:
    """Worry-free and the robot tank follow this spec. Robot Vacuum 5 Pro stays put."""
    current = spec_index("ov21cn.json")
    global_spec = spec_index("ov21gl.json")
    assert set(current) - set(global_spec) == {
        ("action", 20, 4),
        ("property", 20, 10),
        ("property", 22, 1),
        ("property", 22, 2),
    }
    assert set(global_spec) - set(current) == set()
    chinese = require_family(MODEL_MIJIA_5_PRO)
    global_model = require_family(MODEL_ROBOT_VACUUM_5_PRO)
    assert chinese.property_overrides == global_model.property_overrides
    assert chinese.action_overrides == global_model.action_overrides
    assert chinese.state_by_wire == global_model.state_by_wire
    addresses = mapped_addresses(chinese, "property")
    assert addresses[(20, 10)] == "xiaomi_precise_diagnosis"
    assert addresses[(22, 2)] == "xiaomi_self_check_results"
    worry_free = next(
        control
        for control in chinese.controls
        if control.key == "xiaomi_worry_free_mode"
    )
    host_tank = next(
        control for control in chinese.controls if control.key == "xiaomi_host_tank"
    )
    assert [slug for _value, slug in worry_free.options] == [
        "silent_clean",
        "deep_clean",
        "general",
        "butler",
        "pet",
    ]
    assert [value for value, _slug in host_tank.options] == [0, 1, 2, 3, 4]
    global_worry = next(
        control
        for control in global_model.controls
        if control.key == "xiaomi_worry_free_mode"
    )
    assert [slug for _value, slug in global_worry.options][2] == "standard"
    assert 4 not in {
        value
        for value, _slug in next(
            control
            for control in global_model.controls
            if control.key == "xiaomi_host_tank"
        ).options
    }

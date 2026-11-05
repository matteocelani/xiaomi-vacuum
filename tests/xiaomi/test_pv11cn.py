"""Spec coverage for xiaomi.vacuum.pv11cn, the Mijia 6 Max."""

from __future__ import annotations

from custom_components.dreame_vacuum.xiaomi import (
    MODEL_MIJIA_6_MAX,
    MODEL_ROBOT_VACUUM_6_MAX,
)
from custom_components.dreame_vacuum.xiaomi.model import StoredTask
import pytest
from tests.xiaomi.spec_helpers import (
    ROBOT_VACUUM_6_ACTION_REASONS,
    ROBOT_VACUUM_6_PROPERTY_REASONS,
    VACUUM_6_MAX_ACTION_REASONS,
    VACUUM_6_MAX_PROPERTY_REASONS,
    VACUUM_6_MAX_STATE_AFTER_READ,
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

_CASE = SpecCase(
    model=MODEL_MIJIA_6_MAX,
    device_name="Mijia 6 Max",
    spec_filename="pv11cn.json",
    property_reasons=with_reason_overrides(
        VACUUM_6_MAX_PROPERTY_REASONS,
        add={
            (2, 104): ROBOT_VACUUM_6_PROPERTY_REASONS[(2, 104)],
            (2, 105): ROBOT_VACUUM_6_PROPERTY_REASONS[(2, 105)],
            (2, 106): ROBOT_VACUUM_6_PROPERTY_REASONS[(2, 106)],
            (20, 19): "no ha meaning: unnamed field is neither readable nor writable.",
            (23, 1): ROBOT_VACUUM_6_PROPERTY_REASONS[(23, 1)],
            (23, 2): ROBOT_VACUUM_6_PROPERTY_REASONS[(23, 2)],
            (23, 3): ROBOT_VACUUM_6_PROPERTY_REASONS[(23, 3)],
        },
    ),
    action_reasons=with_reason_overrides(
        VACUUM_6_MAX_ACTION_REASONS,
        add={
            (2, 66): ROBOT_VACUUM_6_ACTION_REASONS[(2, 66)],
            (20, 16): ROBOT_VACUUM_6_ACTION_REASONS[(20, 16)],
        },
    ),
    state_after_read=VACUUM_6_MAX_STATE_AFTER_READ,
    classification_counts={
        "pv11cn.json": (155, 132),
        "pv11cn_v1.json": (155, 130),
    },
    spec_type="urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-pv11cn:2",
    reason_prefix_counts={
        "identity": 10,
        "map": 124,
        "needs council": 93,
        "no ha meaning": 35,
    },
    absent_items=(("action", 2, 22),),
    action_spec_filenames=("pv11cn.json", "pv11cn_v1.json"),
    previous_spec_filename="pv11cn_v1.json",
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
    listed = spec_index("pv11cn.json")[("property", 2, 2)].get("value-list")
    assert isinstance(listed, list)
    wires = [item["value"] for item in listed if isinstance(item, dict)]
    assert set(wires) == set(VACUUM_6_MAX_STATE_AFTER_READ)


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


def test_call_clean_is_a_sweep_type_and_the_global_record_stays() -> None:
    """The missing action stays off. Wire 12 decodes, and Robot Vacuum 6 Max is unchanged."""
    current = spec_index("pv11cn.json")
    global_spec = spec_index("pv11gl.json")
    assert ("action", 2, 22) not in current
    assert ("action", 2, 22) in global_spec
    listed = current[("property", 2, 5)].get("value-list")
    assert isinstance(listed, list)
    labels = {
        item["value"]: item["description"] for item in listed if isinstance(item, dict)
    }
    assert labels[12] == "Call Clean"
    chinese = require_family(MODEL_MIJIA_6_MAX)
    base = require_family(MODEL_ROBOT_VACUUM_6_MAX)
    assert chinese.property_overrides == base.property_overrides
    assert chinese.action_overrides == base.action_overrides
    assert chinese.state_by_wire == base.state_by_wire
    assert 12 not in base.task_by_wire
    assert chinese.convert_incoming("TASK_STATUS", 12) == int(StoredTask.AUTO_CLEANING)
    assert base.convert_incoming("TASK_STATUS", 12) == -1
    added = {control.key for control in chinese.controls} - {
        control.key for control in base.controls
    }
    dropped = {control.key for control in base.controls} - {
        control.key for control in chinese.controls
    }
    assert added == {
        "xiaomi_cut_hair_frequency",
        "xiaomi_dust_arrest_power",
        "xiaomi_start_station_self_clean",
        "xiaomi_stop_station_self_clean",
    }
    assert dropped == {"xiaomi_call_clean"}
    assert (2, 22) not in mapped_addresses(chinese, "action")
    assert (2, 66) not in mapped_addresses(chinese, "action")
    assert (20, 16) not in mapped_addresses(chinese, "action")

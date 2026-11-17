"""Spec coverage for xiaomi.vacuum.d102ev, the Mijia M30."""

from __future__ import annotations

from custom_components.xiaomi_robot_vacuum.xiaomi import MODEL_MIJIA_M30, MODEL_X20_PRO
from custom_components.xiaomi_robot_vacuum.xiaomi.model import XiaomiModel
import pytest
from tests.xiaomi.spec_helpers import (
    X20_PRO_ACTION_REASONS,
    X20_PRO_PROPERTY_REASONS,
    X20_PRO_STATE_AFTER_READ,
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

_CASE = SpecCase(
    model=MODEL_MIJIA_M30,
    device_name="Mijia M30",
    spec_filename="d102ev.json",
    property_reasons=X20_PRO_PROPERTY_REASONS,
    action_reasons=with_reason_overrides(X20_PRO_ACTION_REASONS, drop=((20, 3),)),
    state_after_read=X20_PRO_STATE_AFTER_READ,
    classification_counts={"d102ev.json": (97, 77)},
    spec_type="urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-d102ev:1",
    reason_prefix_counts={
        "identity": 5,
        "map": 39,
        "needs council": 23,
        "no ha meaning": 10,
    },
    absent_items=(
        ("action", 10, 8),
        ("action", 20, 3),
        ("property", 2, 76),
        ("property", 2, 77),
        ("property", 2, 78),
        ("property", 10, 10),
        ("property", 10, 11),
        ("property", 10, 12),
        ("property", 10, 13),
        ("property", 10, 14),
    ),
    action_spec_filenames=("d102ev.json",),
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
    listed = spec_index("d102ev.json")[("property", 2, 2)].get("value-list")
    assert isinstance(listed, list)
    wires = [item["value"] for item in listed if isinstance(item, dict)]
    assert set(wires) == set(X20_PRO_STATE_AFTER_READ)


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


def test_shorter_lists_and_hot_water_do_not_change_x20_pro() -> None:
    """Hot water is added. Carpet switches and the dropped values stay off X20 Pro."""
    current = spec_index("d102ev.json")
    global_spec = spec_index("d102gl.json")
    assert set(current) - set(global_spec) == {("property", 2, 41)}
    assert set(global_spec) - set(current) == {
        ("action", 10, 8),
        ("action", 20, 3),
        ("property", 2, 76),
        ("property", 2, 77),
        ("property", 2, 78),
        ("property", 10, 10),
        ("property", 10, 11),
        ("property", 10, 12),
        ("property", 10, 13),
        ("property", 10, 14),
    }
    chinese = require_family(MODEL_MIJIA_M30)
    base = require_family(MODEL_X20_PRO)
    assert chinese.property_overrides == base.property_overrides
    assert chinese.action_overrides == base.action_overrides
    assert chinese.state_by_wire == base.state_by_wire
    assert chinese.task_by_wire == base.task_by_wire

    def options(family: XiaomiModel, key: str) -> list[int]:
        for control in family.controls:
            if control.key == key:
                return [value for value, _slug in control.options]
        raise AssertionError(key)

    assert options(chinese, "xiaomi_mop_wash_frequency") == [0, 1]
    assert options(base, "xiaomi_mop_wash_frequency") == [0, 1, 2]
    assert options(chinese, "xiaomi_carpet_cleaning_method") == [0, 1, 2]
    assert options(base, "xiaomi_carpet_cleaning_method") == [0, 1, 2, 3]
    added = {control.key for control in chinese.controls} - {
        control.key for control in base.controls
    }
    dropped = {control.key for control in base.controls} - {
        control.key for control in chinese.controls
    }
    assert added == {"xiaomi_hot_water_wash"}
    assert dropped == {
        "xiaomi_carpet_deep_cleaning",
        "xiaomi_carpet_discriminate",
        "xiaomi_sweep_carpet_first",
    }

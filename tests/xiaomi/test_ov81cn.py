"""Spec coverage for xiaomi.vacuum.ov81cn, the Mijia Robot Vacuum 4."""

from __future__ import annotations

from custom_components.xiaomi_robot_vacuum.xiaomi import (
    MODEL_MIJIA_ROBOT_VACUUM_4,
    MODEL_S60,
)
import pytest
from tests.xiaomi.spec_helpers import (
    ROBOT_VACUUM_6_ACTION_REASONS,
    ROBOT_VACUUM_6_PROPERTY_REASONS,
    S60_CLASS_ACTION_REASONS,
    S60_CLASS_PROPERTY_REASONS,
    S60_CLASS_STATE_AFTER_READ,
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

_OMITTED_WIRES = frozenset({12, 14, 20, 22, 23, 25, 26, 27})
_STATE_AFTER_READ = {
    wire: state
    for wire, state in S60_CLASS_STATE_AFTER_READ.items()
    if wire not in _OMITTED_WIRES
}

_CASE = SpecCase(
    model=MODEL_MIJIA_ROBOT_VACUUM_4,
    device_name="Mijia Robot Vacuum 4",
    spec_filename="ov81cn.json",
    property_reasons=with_reason_overrides(
        S60_CLASS_PROPERTY_REASONS,
        drop=((2, 103), (22, 1)),
        add={
            (2, 104): ROBOT_VACUUM_6_PROPERTY_REASONS[(2, 104)],
            (2, 105): ROBOT_VACUUM_6_PROPERTY_REASONS[(2, 105)],
            (23, 1): ROBOT_VACUUM_6_PROPERTY_REASONS[(23, 1)],
            (23, 2): ROBOT_VACUUM_6_PROPERTY_REASONS[(23, 2)],
            (23, 3): ROBOT_VACUUM_6_PROPERTY_REASONS[(23, 3)],
        },
    ),
    action_reasons=with_reason_overrides(
        S60_CLASS_ACTION_REASONS,
        drop=((2, 60), (20, 3), (20, 10), (20, 16)),
        add={(2, 66): ROBOT_VACUUM_6_ACTION_REASONS[(2, 66)]},
    ),
    state_after_read=_STATE_AFTER_READ,
    classification_counts={
        "ov81cn.json": (71, 96),
        "ov81cn_v1.json": (71, 93),
    },
    spec_type="urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-ov81cn:2",
    reason_prefix_counts={
        "identity": 10,
        "map": 103,
        "needs council": 54,
        "no ha meaning": 22,
    },
    absent_items=(
        ("action", 2, 44),
        ("action", 2, 60),
        ("action", 20, 3),
        ("action", 20, 10),
        ("action", 20, 16),
        ("property", 2, 68),
        ("property", 2, 76),
        ("property", 2, 77),
        ("property", 2, 78),
        ("property", 2, 103),
        ("property", 2, 109),
        ("property", 22, 1),
        ("property", 22, 2),
    ),
    action_spec_filenames=("ov81cn.json", "ov81cn_v1.json"),
    previous_spec_filename="ov81cn_v1.json",
)

pytestmark = [
    pytest.mark.enable_socket,
    pytest.mark.allow_hosts(["127.0.0.1"]),
]


def test_the_published_spec_is_fully_classified() -> None:
    """Each spec item is mapped or has one explicit omission reason.

    miot-spec.org lists released versions 1 and 2. Version 2 is the latest.
    There is no preview. Version 2 adds the standard-map service.
    """
    assert_spec_is_fully_classified(_CASE)


def test_every_published_status_wire_has_a_shell_state() -> None:
    """The state table covers the status value list and no extra wire."""
    listed = spec_index("ov81cn.json")[("property", 2, 2)].get("value-list")
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


def test_shorter_lists_do_not_change_s60() -> None:
    """Summon, station-assist, and the dock extras stay on S60."""
    current = require_family(MODEL_MIJIA_ROBOT_VACUUM_4)
    base = require_family(MODEL_S60)
    assert current.property_overrides == base.property_overrides
    assert current.action_overrides == base.action_overrides
    assert set(base.state_by_wire) - set(current.state_by_wire) == {
        12,
        14,
        20,
        22,
        23,
        25,
        26,
        27,
    }
    assert set(base.task_by_wire) - set(current.task_by_wire) == {4, 5, 6, 9, 11}
    dropped = {control.key for control in base.controls} - {
        control.key for control in current.controls
    }
    assert dropped == {
        "xiaomi_carpet_deep_cleaning",
        "xiaomi_carpet_discriminate",
        "xiaomi_edge_sweep_frequency",
        "xiaomi_self_check_results",
        "xiaomi_stop_cut_hair",
        "xiaomi_sweep_carpet_first",
        "xiaomi_vibration_mop",
    }

    def values(model_controls: object, key: str) -> list[int]:
        for control in model_controls:
            if control.key == key:
                return [value for value, _slug in control.options]
        raise AssertionError(key)

    assert values(current.controls, "xiaomi_clean_times") == [1, 2]
    assert values(base.controls, "xiaomi_clean_times") == [1, 2, 3]
    assert values(current.controls, "xiaomi_worry_free_mode") == [0, 1, 2]
    assert values(base.controls, "xiaomi_worry_free_mode") == [0, 1, 2, 3, 4]

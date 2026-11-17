"""Spec coverage for xiaomi.vacuum.d101, the Mijia H40."""

from __future__ import annotations

from custom_components.xiaomi_robot_vacuum.dreame.types import DreameVacuumState
from custom_components.xiaomi_robot_vacuum.xiaomi import MODEL_MIJIA_H40, MODEL_X20_PRO
import pytest
from tests.xiaomi.spec_helpers import (
    ROBOT_VACUUM_6_ACTION_REASONS,
    S60_CLASS_ACTION_REASONS,
    S60_CLASS_PROPERTY_REASONS,
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

_STATE_AFTER_READ = {
    **X20_PRO_STATE_AFTER_READ,
    22: DreameVacuumState.WASHING,
    23: DreameVacuumState.CHARGING_COMPLETED,
    24: DreameVacuumState.RETURNING,
}

_CASE = SpecCase(
    model=MODEL_MIJIA_H40,
    device_name="Mijia H40",
    spec_filename="d101.json",
    property_reasons=with_reason_overrides(
        X20_PRO_PROPERTY_REASONS,
        drop=((2, 53), (15, 1), (15, 5), (15, 6)),
        add={(2, 99): S60_CLASS_PROPERTY_REASONS[(2, 99)]},
    ),
    action_reasons=with_reason_overrides(
        X20_PRO_ACTION_REASONS,
        drop=((15, 1), (15, 2), (20, 3)),
        add={
            (2, 52): ROBOT_VACUUM_6_ACTION_REASONS[(2, 52)],
            (2, 53): ROBOT_VACUUM_6_ACTION_REASONS[(2, 53)],
            (2, 54): ROBOT_VACUUM_6_ACTION_REASONS[(2, 54)],
            (2, 55): ROBOT_VACUUM_6_ACTION_REASONS[(2, 55)],
            (2, 56): S60_CLASS_ACTION_REASONS[(2, 56)],
        },
    ),
    state_after_read=_STATE_AFTER_READ,
    classification_counts={
        "d101.json": (80, 76),
        "d101_v1.json": (76, 70),
        "d101_v2.json": (79, 75),
    },
    spec_type="urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-d101:3",
    reason_prefix_counts={
        "identity": 15,
        "map": 128,
        "needs council": 57,
        "no ha meaning": 21,
    },
    absent_items=(
        ("action", 2, 18),
        ("action", 15, 1),
        ("action", 15, 2),
        ("action", 18, 1),
        ("action", 19, 1),
        ("action", 20, 3),
        ("property", 2, 32),
        ("property", 2, 33),
        ("property", 2, 35),
        ("property", 2, 36),
        ("property", 2, 53),
        ("property", 2, 59),
        ("property", 2, 62),
        ("property", 2, 71),
        ("property", 2, 77),
        ("property", 3, 3),
        ("property", 15, 1),
        ("property", 15, 5),
        ("property", 15, 6),
        ("property", 18, 1),
        ("property", 19, 1),
    ),
    action_spec_filenames=("d101.json", "d101_v1.json", "d101_v2.json"),
)

pytestmark = [
    pytest.mark.enable_socket,
    pytest.mark.allow_hosts(["127.0.0.1"]),
]


def test_the_published_spec_is_fully_classified() -> None:
    """Each spec item is mapped or has one explicit omission reason.

    miot-spec.org lists released versions 1, 2, and 3. Version 3 is the latest.
    There is no preview.
    """
    assert_spec_is_fully_classified(_CASE)


def test_every_published_status_wire_has_a_shell_state() -> None:
    """The state table covers the status value list and no extra wire."""
    listed = spec_index("d101.json")[("property", 2, 2)].get("value-list")
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


def test_dust_voice_and_detergent_stay_on_x20_pro() -> None:
    """Station assist is added. Dust collection, voice, and detergent stay off."""
    current = require_family(MODEL_MIJIA_H40)
    base = require_family(MODEL_X20_PRO)
    assert set(base.property_overrides) - set(current.property_overrides) == {
        "AUTO_DUST_COLLECTING",
        "AUTO_EMPTY_FREQUENCY",
        "DETERGENT_LEFT",
    }
    assert set(base.action_overrides) - set(current.action_overrides) == {
        "RESET_DETERGENT",
        "START_AUTO_EMPTY",
    }
    assert set(current.state_by_wire) - set(base.state_by_wire) == {22, 23, 24}
    assert current.task_by_wire == base.task_by_wire
    added = {control.key for control in current.controls} - {
        control.key for control in base.controls
    }
    dropped = {control.key for control in base.controls} - {
        control.key for control in current.controls
    }
    assert added == {
        "xiaomi_start_station_cleaning",
        "xiaomi_stop_working",
        "xiaomi_sweep_before_mop",
        "xiaomi_sweep_mop_status",
    }
    assert dropped == {
        "xiaomi_auto_water_change",
        "xiaomi_auto_water_change_installed",
        "xiaomi_cancel_water_check",
        "xiaomi_carpet_discriminate",
        "xiaomi_current_voice",
        "xiaomi_detergent_delivery",
        "xiaomi_detergent_level",
        "xiaomi_detergent_reminder",
        "xiaomi_detergent_self_delivery",
        "xiaomi_download_progress",
        "xiaomi_download_status",
        "xiaomi_dust_bag_life",
        "xiaomi_dust_bag_time_left",
        "xiaomi_reset_dust_bag",
        "xiaomi_start_water_check",
        "xiaomi_use_detergent",
        "xiaomi_voltage",
        "xiaomi_water_check_status",
    }

    def values(model_controls: object, key: str) -> list[int]:
        for control in model_controls:
            if control.key == key:
                return [value for value, _slug in control.options]
        raise AssertionError(key)

    assert values(current.controls, "xiaomi_drying_time") == list(range(1, 12))
    assert values(base.controls, "xiaomi_drying_time") == [1, 2, 3]
    assert values(current.controls, "xiaomi_mop_wash_frequency") == [0, 1]
    assert values(base.controls, "xiaomi_mop_wash_frequency") == [0, 1, 2]

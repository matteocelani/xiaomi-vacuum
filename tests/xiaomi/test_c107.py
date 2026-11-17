"""Spec coverage for xiaomi.vacuum.c107, the Mijia M30 Pro."""

from __future__ import annotations

from custom_components.xiaomi_robot_vacuum.xiaomi import (
    MODEL_MIJIA_M30,
    MODEL_MIJIA_M30_PRO,
)
import pytest
from tests.xiaomi.spec_helpers import (
    ROBOT_VACUUM_5_ACTION_REASONS,
    ROBOT_VACUUM_5_PROPERTY_REASONS,
    ROBOT_VACUUM_6_PROPERTY_REASONS,
    S60_CLASS_ACTION_REASONS,
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
    model=MODEL_MIJIA_M30_PRO,
    device_name="Mijia M30 Pro",
    spec_filename="c107.json",
    property_reasons=with_reason_overrides(
        X20_PRO_PROPERTY_REASONS,
        add={
            (2, 56): ROBOT_VACUUM_6_PROPERTY_REASONS[(2, 56)],
            (17, 1): ROBOT_VACUUM_5_PROPERTY_REASONS[(17, 1)],
            (17, 2): ROBOT_VACUUM_5_PROPERTY_REASONS[(17, 2)],
        },
    ),
    action_reasons=with_reason_overrides(
        X20_PRO_ACTION_REASONS,
        drop=((20, 3),),
        add={
            (2, 10): S60_CLASS_ACTION_REASONS[(2, 10)],
            (17, 1): ROBOT_VACUUM_5_ACTION_REASONS[(17, 1)],
        },
    ),
    state_after_read=X20_PRO_STATE_AFTER_READ,
    classification_counts={
        "c107.json": (117, 88),
        "c107_v1.json": (113, 83),
    },
    spec_type="urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-c107:2",
    reason_prefix_counts={
        "identity": 10,
        "map": 81,
        "needs council": 60,
        "no ha meaning": 20,
    },
    action_spec_filenames=("c107.json", "c107_v1.json"),
)

pytestmark = [
    pytest.mark.enable_socket,
    pytest.mark.allow_hosts(["127.0.0.1"]),
]


def test_the_published_spec_is_fully_classified() -> None:
    """Each spec item is mapped or has one explicit omission reason.

    miot-spec.org lists released versions 1 and 2. Version 2 is the latest.
    There is no preview. Version 1 stops cut-hair frequency at 3.
    """
    assert_spec_is_fully_classified(_CASE)


def test_every_published_status_wire_has_a_shell_state() -> None:
    """The state table covers the status value list and no extra wire."""
    listed = spec_index("c107.json")[("property", 2, 2)].get("value-list")
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


def test_camera_switches_do_not_change_mijia_m30() -> None:
    """Hair cutting and the camera switches are added. Edge sweep uses the S40 order."""
    current = require_family(MODEL_MIJIA_M30_PRO)
    base = require_family(MODEL_MIJIA_M30)
    assert set(current.property_overrides) - set(base.property_overrides) == {
        "DETERGENT_TIME_LEFT"
    }
    assert current.action_overrides == base.action_overrides
    assert current.state_by_wire == base.state_by_wire
    added = {control.key for control in current.controls} - {
        control.key for control in base.controls
    }
    assert added == {
        "xiaomi_ai_cleaning",
        "xiaomi_ai_managed_cleaning",
        "xiaomi_calibrate_imu",
        "xiaomi_call_clean",
        "xiaomi_carpet_deep_cleaning",
        "xiaomi_carpet_discriminate",
        "xiaomi_cut_hair",
        "xiaomi_cut_hair_frequency",
        "xiaomi_defecation_detection",
        "xiaomi_dirt_detection",
        "xiaomi_floor_material_detection",
        "xiaomi_liquid_dirt_detection",
        "xiaomi_mop_auto_lift",
        "xiaomi_object_detection",
        "xiaomi_room_detection",
        "xiaomi_solid_dirt_detection",
        "xiaomi_start_cut_hair",
        "xiaomi_stop_cut_hair",
        "xiaomi_sweep_ai_detection",
    }

    def slugs(model_controls: object, key: str) -> tuple[str, ...]:
        for control in model_controls:
            if control.key == key:
                return tuple(slug for _value, slug in control.options)
        raise AssertionError(key)

    assert slugs(current.controls, "xiaomi_edge_sweep_frequency") == (
        "seven_sweeps",
        "every_time",
    )
    assert slugs(base.controls, "xiaomi_edge_sweep_frequency") == (
        "every_time",
        "seven_sweeps",
    )

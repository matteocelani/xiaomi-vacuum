"""Spec coverage for xiaomi.vacuum.qv12cn, the Mijia Robot Vacuum 7 Max."""

from __future__ import annotations

from custom_components.dreame_vacuum.xiaomi import (
    MODEL_MIJIA_7_MAX,
    MODEL_ROBOT_VACUUM_6_MAX,
    resolve_family,
)
from custom_components.dreame_vacuum.xiaomi.mapping import _FAMILIES
from custom_components.dreame_vacuum.xiaomi.model import StoredTask, regional_variant
from custom_components.dreame_vacuum.xiaomi.pv11gl import ROBOT_VACUUM_6_MAX
from custom_components.dreame_vacuum.xiaomi.qv12cn import MIJIA_7_MAX
import pytest
from tests.xiaomi.spec_helpers import (
    MIJIA_7_MAX_ACTION_REASONS,
    MIJIA_7_MAX_PROPERTY_REASONS,
    MIJIA_7_MAX_STATE_AFTER_READ,
    SpecCase,
    assert_controls_have_english_names,
    assert_controls_match_spec,
    assert_spec_is_fully_classified,
    comparable_spec_item,
    exercise_control_values,
    exercise_mapped_actions,
    exercise_mapped_property_reads,
    exercise_rejected_control_traffic,
    exercise_status_wires,
    exercise_writable_values,
    mapped_addresses,
    require_family,
    spec_index,
)

_CASE = SpecCase(
    model=MODEL_MIJIA_7_MAX,
    device_name="Mijia 7 Max",
    spec_filename="qv12cn.json",
    property_reasons=MIJIA_7_MAX_PROPERTY_REASONS,
    action_reasons=MIJIA_7_MAX_ACTION_REASONS,
    state_after_read=MIJIA_7_MAX_STATE_AFTER_READ,
    classification_counts={"qv12cn.json": (153, 136)},
    spec_type="urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-qv12cn:1",
    reason_prefix_counts={
        "identity": 5,
        "map": 62,
        "needs council": 52,
        "no ha meaning": 17,
    },
    absent_items=(
        ("action", 2, 9),
        ("action", 20, 7),
        ("property", 2, 47),
        ("property", 2, 48),
        ("property", 2, 92),
        ("property", 10, 11),
        ("property", 10, 12),
        ("property", 18, 3),
        ("property", 18, 4),
        ("property", 19, 2),
        ("property", 20, 9),
        ("property", 20, 11),
        ("property", 20, 12),
        ("property", 21, 4),
    ),
    action_spec_filenames=("qv12cn.json",),
)
_ADDED_VERSUS_6_MAX = {
    ("action", 2, 63),
    ("action", 2, 64),
    ("action", 2, 66),
    ("action", 16, 1),
    ("action", 17, 1),
    ("action", 20, 16),
    ("property", 2, 37),
    ("property", 2, 55),
    ("property", 2, 69),
    ("property", 2, 104),
    ("property", 2, 105),
    ("property", 2, 106),
    ("property", 2, 108),
    ("property", 2, 110),
    ("property", 17, 1),
    ("property", 17, 2),
    ("property", 20, 16),
    ("property", 20, 17),
    ("property", 20, 18),
    ("property", 20, 19),
    ("property", 23, 1),
    ("property", 23, 2),
    ("property", 23, 3),
    ("property", 25, 1),
    ("property", 25, 2),
    ("property", 25, 4),
    ("property", 25, 5),
    ("property", 26, 1),
}
_REMOVED_VERSUS_6_MAX = {
    ("action", 2, 9),
    ("action", 20, 7),
    ("property", 2, 47),
    ("property", 2, 48),
    ("property", 2, 92),
    ("property", 10, 11),
    ("property", 10, 12),
    ("property", 18, 3),
    ("property", 18, 4),
    ("property", 19, 2),
    ("property", 20, 9),
    ("property", 20, 11),
    ("property", 20, 12),
    ("property", 21, 4),
}
_CHANGED_VERSUS_6_MAX = {
    ("action", 20, 11),
    ("action", 20, 15),
    ("property", 2, 2),
    ("property", 2, 5),
    ("property", 2, 8),
    ("property", 2, 30),
    ("property", 2, 61),
}
_REGISTERED_BEFORE_7_MAX = 36

pytestmark = [
    pytest.mark.enable_socket,
    pytest.mark.allow_hosts(["127.0.0.1"]),
]


def test_the_published_spec_is_fully_classified() -> None:
    """Each spec item is mapped or has one explicit omission reason.

    miot-spec.org lists released version 1 only, published 2026-10-09.
    The global qv12gl spec is preview version 1 and is not registered.
    """
    assert_spec_is_fully_classified(_CASE)


def test_every_published_status_and_sweep_wire_is_decoded() -> None:
    """Status and sweep-type tables cover the published lists and no extra wire."""
    status = spec_index("qv12cn.json")[("property", 2, 2)].get("value-list")
    sweep = spec_index("qv12cn.json")[("property", 2, 5)].get("value-list")
    assert isinstance(status, list)
    assert isinstance(sweep, list)
    status_wires = [item["value"] for item in status if isinstance(item, dict)]
    sweep_wires = [item["value"] for item in sweep if isinstance(item, dict)]
    family = require_family(MODEL_MIJIA_7_MAX)
    assert status_wires == [
        *range(1, 15),
        18,
        19,
        20,
        21,
        25,
        26,
    ]
    assert set(status_wires) == set(MIJIA_7_MAX_STATE_AFTER_READ)
    assert set(family.state_by_wire) == set(status_wires)
    assert sweep_wires == [1, 2, 3, 7, 8, 10]
    assert set(family.task_by_wire) == set(sweep_wires)
    assert family.convert_incoming("TASK_STATUS", 10) == int(StoredTask.FAST_MAPPING)
    assert family.convert_incoming("TASK_STATUS", 8) == int(StoredTask.AUTO_CLEANING)


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


def test_video_password_and_check_entry_are_not_mapped() -> None:
    """Password actions and the parameterized check entry stay off the wire."""
    actions = mapped_addresses(require_family(MODEL_MIJIA_7_MAX), "action")
    assert (21, 6) not in actions
    assert (21, 7) not in actions
    assert (21, 8) not in actions
    assert (20, 11) not in actions
    assert (2, 66) not in actions
    assert (17, 1) not in actions
    assert (20, 16) not in actions


def test_the_record_is_its_own_station_profile_not_a_6_max_alias() -> None:
    """Address overlap with Robot Vacuum 6 Max is too wide for a clean variant."""
    current = spec_index("qv12cn.json")
    vacuum_6_max = spec_index("pv11gl.json")
    assert set(current) - set(vacuum_6_max) == _ADDED_VERSUS_6_MAX
    assert set(vacuum_6_max) - set(current) == _REMOVED_VERSUS_6_MAX
    codes = ("qv12cn", "pv11gl")
    for key in (set(current) & set(vacuum_6_max)) - _CHANGED_VERSUS_6_MAX:
        assert comparable_spec_item(current[key], codes) == comparable_spec_item(
            vacuum_6_max[key], codes
        ), key
    chinese = require_family(MODEL_MIJIA_7_MAX)
    base = require_family(MODEL_ROBOT_VACUUM_6_MAX)
    assert chinese is MIJIA_7_MAX
    assert base is ROBOT_VACUUM_6_MAX
    assert chinese is not base
    assert "DETERGENT_TIME_LEFT" not in chinese.property_overrides
    assert "DETERGENT_TIME_LEFT" in base.property_overrides
    assert "START_CUSTOM" not in chinese.action_overrides
    assert "START_CUSTOM" in base.action_overrides
    assert (18, 4) not in mapped_addresses(chinese, "property")
    assert (2, 9) not in mapped_addresses(chinese, "action")
    # Floor through c104. A later model may register without changing this.
    assert len(_FAMILIES) >= _REGISTERED_BEFORE_7_MAX + 6


def test_preview_global_7_max_is_not_registered() -> None:
    """A copy of this record is what a released qv12gl would register later."""
    base = require_family(MODEL_MIJIA_7_MAX)
    copied = regional_variant(base, "xiaomi.vacuum.qv12gl")
    assert copied is not base
    assert copied.model == "xiaomi.vacuum.qv12gl"
    assert copied.property_overrides == base.property_overrides
    assert copied.action_overrides == base.action_overrides
    assert copied.state_by_wire == base.state_by_wire
    assert copied.task_by_wire == base.task_by_wire
    assert copied.controls == base.controls
    assert resolve_family("xiaomi.vacuum.qv12gl") is None
    assert require_family(MODEL_MIJIA_7_MAX) is base

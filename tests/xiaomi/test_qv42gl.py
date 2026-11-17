"""Spec coverage for xiaomi.vacuum.qv42gl, the Xiaomi Robot Vacuum H50 Roller."""

from __future__ import annotations

from typing import Final

from custom_components.xiaomi_robot_vacuum.xiaomi import MODEL_H50_ROLLER
import pytest
from tests.xiaomi.spec_helpers import (
    ROBOT_VACUUM_6_ACTION_REASONS,
    ROBOT_VACUUM_6_PROPERTY_REASONS,
    S60_CLASS_STATE_AFTER_READ,
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

_PROPERTY_REASONS: Final = {
    key: reason
    for key, reason in ROBOT_VACUUM_6_PROPERTY_REASONS.items()
    if ("property", key[0], key[1]) in spec_index("qv42gl.json")
}
_ACTION_REASONS: Final = {
    key: reason
    for key, reason in ROBOT_VACUUM_6_ACTION_REASONS.items()
    if ("action", key[0], key[1]) in spec_index("qv42gl.json")
}

_CASE = SpecCase(
    model=MODEL_H50_ROLLER,
    device_name="H50 Roller",
    spec_filename="qv42gl.json",
    property_reasons=_PROPERTY_REASONS,
    action_reasons=_ACTION_REASONS,
    state_after_read=S60_CLASS_STATE_AFTER_READ,
    classification_counts={"qv42gl.json": (109, 100)},
    spec_type="urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-qv42gl:1",
    reason_prefix_counts={
        "identity": 5,
        "map": 53,
        "needs council": 29,
        "no ha meaning": 13,
    },
    absent_items=(
        ("action", 2, 21),
        ("action", 2, 45),
        ("property", 2, 35),
        ("property", 2, 45),
        ("property", 2, 79),
        ("property", 18, 1),
        ("property", 23, 1),
    ),
    action_spec_filenames=("qv42gl.json",),
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
    """The state table covers status 1 through 27 and no extra wire."""
    listed = spec_index("qv42gl.json")[("property", 2, 2)].get("value-list")
    assert isinstance(listed, list)
    wires = [item["value"] for item in listed if isinstance(item, dict)]
    assert wires == [*range(1, 28)]
    assert set(wires) == set(S60_CLASS_STATE_AFTER_READ)


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


def test_published_spec_matches_h50_pro_roller_except_the_station_block() -> None:
    """H50 Roller adds mop-only and summon states, and drops the water station."""
    current = spec_index("qv42gl.json")
    pro = spec_index("qv41gl.json")
    assert set(current) - set(pro) == {
        ("action", 2, 5),
        ("action", 2, 19),
        ("action", 16, 1),
        ("property", 2, 44),
        ("property", 2, 82),
        ("property", 2, 97),
        ("property", 2, 98),
    }
    assert set(pro) - set(current) == {
        ("action", 2, 21),
        ("action", 2, 45),
        ("action", 2, 46),
        ("action", 2, 49),
        ("action", 2, 52),
        ("action", 2, 53),
        ("action", 2, 54),
        ("action", 2, 55),
        ("action", 2, 57),
        ("action", 2, 59),
        ("action", 2, 61),
        ("action", 2, 66),
        ("action", 20, 4),
        ("property", 2, 35),
        ("property", 2, 36),
        ("property", 2, 41),
        ("property", 2, 45),
        ("property", 2, 53),
        ("property", 2, 54),
        ("property", 2, 56),
        ("property", 2, 62),
        ("property", 2, 84),
        ("property", 2, 100),
        ("property", 2, 104),
        ("property", 2, 105),
        ("property", 20, 4),
        ("property", 20, 5),
        ("property", 23, 1),
        ("property", 23, 2),
        ("property", 23, 3),
    }
    changed = {
        ("property", 2, 2),
        ("property", 2, 4),
        ("property", 2, 83),
    }
    codes = ("qv42gl", "qv41gl")
    for key in (set(current) & set(pro)) - changed:
        assert comparable_spec_item(current[key], codes) == comparable_spec_item(
            pro[key], codes
        ), key


_CLEANING_MODE_WIRES: Final = (1, 2, 3, 4)


def test_cleaning_mode_publishes_mop_only() -> None:
    """The Dreame select is safe because the spec publishes mop-only as wire 2."""
    listed = spec_index("qv42gl.json")[("property", 2, 4)].get("value-list")
    assert isinstance(listed, list)
    assert [item["value"] for item in listed if isinstance(item, dict)] == list(
        _CLEANING_MODE_WIRES
    )
    family = require_family(MODEL_H50_ROLLER)
    assert "CLEANING_MODE" in family.property_overrides
    properties = mapped_addresses(family, "property")
    actions = mapped_addresses(family, "action")
    assert properties[(2, 4)] == "CLEANING_MODE"
    assert properties[(2, 44)] == "xiaomi_mop_auto_lift"
    assert properties[(24, 3)] == "xiaomi_roller_outswing"
    assert actions[(2, 5)] == "xiaomi_start_mop"
    assert actions[(16, 1)] == "xiaomi_calibrate_imu"
    assert (2, 21) not in actions

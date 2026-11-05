"""Spec coverage for xiaomi.vacuum.pv21gl, the Xiaomi Robot Vacuum 6 Pro."""

from __future__ import annotations

from custom_components.dreame_vacuum.xiaomi import MODEL_ROBOT_VACUUM_6_PRO
import pytest
from tests.xiaomi.spec_helpers import (
    VACUUM_6_PRO_ACTION_REASONS as _ACTION_REASONS,
    VACUUM_6_PRO_PROPERTY_REASONS as _PROPERTY_REASONS,
    VACUUM_6_PRO_STATE_AFTER_READ as _STATE_AFTER_READ,
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
    normalize_spec,
    require_family,
    spec_index,
)

_CASE = SpecCase(
    model=MODEL_ROBOT_VACUUM_6_PRO,
    device_name="Robot Vacuum 6 Pro",
    spec_filename="pv21gl.json",
    property_reasons=_PROPERTY_REASONS,
    action_reasons=_ACTION_REASONS,
    state_after_read=_STATE_AFTER_READ,
    classification_counts={"pv21gl.json": (149, 123)},
    spec_type="urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-pv21gl:1",
    reason_prefix_counts={
        "identity": 5,
        "map": 59,
        "needs council": 43,
        "no ha meaning": 16,
    },
    absent_items=(
        ("action", 9, 1),
        ("action", 20, 16),
        ("property", 9, 1),
        ("property", 9, 2),
    ),
    action_spec_filenames=("pv21gl.json",),
)

pytestmark = [
    pytest.mark.enable_socket,
    pytest.mark.allow_hosts(["127.0.0.1"]),
]


def test_the_published_spec_is_fully_classified() -> None:
    """Each spec item is mapped or has one explicit omission reason.

    Released lists publish version 1 only. Unpublished version 2 is not mapped.
    """
    assert_spec_is_fully_classified(_CASE)


def test_every_published_status_wire_has_a_shell_state() -> None:
    """The state table covers the status value list and no extra wire."""
    listed = spec_index("pv21gl.json")[("property", 2, 2)].get("value-list")
    assert isinstance(listed, list)
    wires = [item["value"] for item in listed if isinstance(item, dict)]
    assert wires == [*range(1, 27)]
    assert set(wires) == set(_STATE_AFTER_READ)


def test_video_password_actions_are_not_mapped() -> None:
    """Password actions stay off the wire. There is no confirmation flow."""
    actions = mapped_addresses(require_family(MODEL_ROBOT_VACUUM_6_PRO), "action")
    assert (21, 6) not in actions
    assert (21, 7) not in actions
    assert (21, 8) not in actions


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


def test_published_spec_matches_robot_vacuum_6_max_except_mop_and_status() -> None:
    """Version 1 drops mop life and changes status and worry-free only."""
    current = spec_index("pv21gl.json")
    vacuum_6_max = spec_index("pv11gl.json")
    assert set(vacuum_6_max) - set(current) == {
        ("action", 9, 1),
        ("property", 9, 1),
        ("property", 9, 2),
    }
    assert set(current) - set(vacuum_6_max) == set()
    changed = {
        ("property", 2, 2),
        ("property", 2, 83),
    }
    codes = ("pv21gl", "pv11gl")
    for key in (set(current) & set(vacuum_6_max)) - changed:
        assert normalize_spec(current[key], codes) == normalize_spec(
            vacuum_6_max[key], codes
        ), key
    status = current[("property", 2, 2)].get("value-list")
    assert isinstance(status, list)
    assert [item["value"] for item in status if isinstance(item, dict)] == [
        *range(1, 27)
    ]
    worry_free = current[("property", 2, 83)]
    assert _values(worry_free) == [0, 1, 2, 3, 4]
    assert _descriptions(worry_free)[-1].strip() == "Pet"


def test_mop_life_addresses_are_not_mapped() -> None:
    """An empty mop service must not be read or reset."""
    family = require_family(MODEL_ROBOT_VACUUM_6_PRO)
    properties = mapped_addresses(family, "property")
    actions = mapped_addresses(family, "action")
    assert (9, 1) not in properties
    assert (9, 2) not in properties
    assert (9, 1) not in actions


def _values(spec: dict[str, object]) -> list[object]:
    listed = spec.get("value-list")
    assert isinstance(listed, list)
    return [item["value"] for item in listed if isinstance(item, dict)]


def _descriptions(spec: dict[str, object]) -> list[str]:
    listed = spec.get("value-list")
    assert isinstance(listed, list)
    return [str(item["description"]) for item in listed if isinstance(item, dict)]

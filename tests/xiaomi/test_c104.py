"""Spec coverage for xiaomi.vacuum.c104, the Mijia Sweep Mop 3."""

from __future__ import annotations

from custom_components.dreame_vacuum.dreame.types import DreameVacuumState
from custom_components.dreame_vacuum.xiaomi import (
    MODEL_E10,
    MODEL_MIJIA_SWEEP_MOP_3,
    MODEL_S12,
    MODEL_S20,
)
from custom_components.dreame_vacuum.xiaomi.b106eu import S12
from custom_components.dreame_vacuum.xiaomi.controls import ValueKind
from custom_components.dreame_vacuum.xiaomi.profile import STATION_PROPERTIES
from custom_components.dreame_vacuum.xiaomi.sweep import SWEEP_CONTROLS, SWEEP_STATES
import pytest
from tests.xiaomi.spec_helpers import (
    SWEEP_ACTION_REASONS,
    SWEEP_PROPERTY_REASONS,
    SWEEP_STATE_AFTER_READ,
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
    load_spec_document,
    require_family,
    spec_index,
    spec_items,
    with_reason_overrides,
)

_PROPERTY_REASONS = with_reason_overrides(
    SWEEP_PROPERTY_REASONS,
    drop=((7, 48), (7, 49), (14, 1), (14, 2), (14, 3), (14, 4), (14, 5), (14, 6)),
    add={
        (2, 9): "map: restricted walls stay unmapped until map support.",
        (2, 10): "map: room ids stay unmapped until map support.",
        (7, 38): "no ha meaning: clean preference type is an action parameter.",
        (7, 39): "no ha meaning: clean preference switch is an action parameter.",
        (7, 40): "no ha meaning: clean preference is neither readable nor writable.",
        (7, 41): "no ha meaning: clean preference switch is an action parameter.",
        (7, 46): "no ha meaning: the sd flag is neither readable nor writable.",
        (7, 47): "needs council: write-only carpet avoid has no readable state.",
        (7, 55): "map: map encryption stays unmapped until map support.",
        (8, 20): "no ha meaning: current order count is neither readable nor writable.",
        (13, 1): "needs council: standard filter life repeats the named sweep filter.",
        (13, 2): "needs council: standard filter time repeats the named sweep filter.",
        (
            14,
            1,
        ): "needs council: the two brush services are identical, so neither is mapped.",
        (
            14,
            2,
        ): "needs council: the two brush services are identical, so neither is mapped.",
        (
            15,
            1,
        ): "needs council: the two brush services are identical, so neither is mapped.",
        (
            15,
            2,
        ): "needs council: the two brush services are identical, so neither is mapped.",
        (16, 1): "needs council: standard mop life repeats the named sweep mop.",
        (16, 2): "needs council: standard mop time repeats the named sweep mop.",
    },
)
_ACTION_REASONS = with_reason_overrides(
    SWEEP_ACTION_REASONS,
    drop=((14, 1), (14, 2), (14, 3), (14, 4)),
    add={
        (2, 7): "map: room sweep takes a room-id parameter.",
        (7, 4): "needs council: setting a clean preference takes an opaque parameter.",
        (7, 5): "needs council: reading a clean preference takes an opaque parameter.",
        (7, 6): "needs council: setting a preference type takes an opaque parameter.",
        (7, 8): "needs council: erasing a preference takes an opaque parameter.",
        (7, 9): "needs council: setting a clean preference takes an opaque parameter.",
        (7, 10): "needs council: reading a clean preference takes an opaque parameter.",
        (9, 9): "map: point clean stays unmapped until map support.",
        (13, 1): "needs council: filter reset stays on the sweep consumable action.",
        (14, 1): "needs council: the two brush resets cannot be told apart.",
        (15, 1): "needs council: the two brush resets cannot be told apart.",
        (16, 1): "needs council: mop reset stays on the sweep consumable action.",
    },
)
_CASE = SpecCase(
    model=MODEL_MIJIA_SWEEP_MOP_3,
    device_name="Mijia Sweep Mop 3",
    spec_filename="c104.json",
    property_reasons=_PROPERTY_REASONS,
    action_reasons=_ACTION_REASONS,
    state_after_read=SWEEP_STATE_AFTER_READ,
    classification_counts={"c104.json": (42, 153)},
    spec_type="urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-c104:1",
    reason_prefix_counts={
        "identity": 5,
        "map": 66,
        "needs council": 65,
        "no ha meaning": 17,
    },
    checked_events=(
        (3, 1),
        (3, 2),
        (7, 1),
        (7, 2),
        (7, 3),
        (7, 4),
        (8, 1),
        (8, 2),
        (10, 1),
        (10, 2),
        (10, 3),
        (10, 4),
        (10, 5),
        (10, 6),
        (10, 7),
    ),
    state_wire_eight=int(DreameVacuumState.UPGRADING),
    station_shell=False,
)

pytestmark = [
    pytest.mark.enable_socket,
    pytest.mark.allow_hosts(["127.0.0.1"]),
]


def _addresses(filename: str) -> set[tuple[str, int, int]]:
    """Return property and action addresses from one spec fixture."""
    return {
        (kind, siid, iid)
        for kind, siid, iid, _spec in spec_items(filename)
        if kind != "event"
    }


def _service(filename: str, siid: int) -> dict[str, object]:
    """Return one service object from a spec fixture."""
    loaded = load_spec_document(filename)
    services = loaded["services"]
    assert isinstance(services, list)
    for service in services:
        assert isinstance(service, dict)
        if service["iid"] == siid:
            return service
    raise AssertionError(siid)


def test_the_published_spec_is_fully_classified() -> None:
    """Every released spec item is mapped or has one explicit omission reason.

    miot-spec.org lists released version 1. Version 2 is debug and is not used.
    """
    assert_spec_is_fully_classified(_CASE)


def test_released_addresses_overlap_the_sweep_profile() -> None:
    """The spec shares the sweep layout and not the station layout."""
    current = _addresses("c104.json")
    sweep = _addresses("b112.json")
    station = _addresses("d109gl.json")
    s12 = _addresses("b106eu.json")
    assert len(current & sweep) / len(current | sweep) > 0.70
    assert len(current & station) / len(current | station) < 0.25
    assert len(current & s12) / len(current | s12) > 0.90
    status = spec_index("c104.json")[("property", 2, 1)]["value-list"]
    sweep_status = spec_index("b112.json")[("property", 2, 1)]["value-list"]
    s12_status = spec_index("b106eu.json")[("property", 2, 1)]["value-list"]
    assert isinstance(status, list)
    assert isinstance(sweep_status, list)
    assert isinstance(s12_status, list)
    assert status[:8] == sweep_status[:8]
    assert status[8]["description"] == "Upgrade"
    assert status[6]["description"] == "Sweeping and Mopping"
    assert status[7]["description"] == "Mopping"
    assert s12_status[6]["description"] == "Mopping"
    assert status != s12_status


def test_the_record_keeps_s12_addresses_and_restores_sweep_status() -> None:
    """Addresses stay on S12. Status wires 6 and 7 and the alarm list do not."""
    family = require_family(MODEL_MIJIA_SWEEP_MOP_3)
    s12 = require_family(MODEL_S12)
    e10 = require_family(MODEL_E10)
    s20 = require_family(MODEL_S20)
    assert s12 is S12
    assert family.property_overrides == s12.property_overrides
    assert family.action_overrides == s12.action_overrides
    assert family.property_overrides == e10.property_overrides
    assert family.property_overrides != STATION_PROPERTIES
    assert family.state_by_wire == SWEEP_STATES
    assert s12.state_by_wire != SWEEP_STATES
    assert family.state_by_wire != s20.state_by_wire
    assert family.convert_incoming("STATE", 6) == int(
        DreameVacuumState.SWEEPING_AND_MOPPING
    )
    assert family.convert_incoming("STATE", 7) == int(DreameVacuumState.MOPPING)
    assert s12.convert_incoming("STATE", 6) == int(DreameVacuumState.MOPPING)
    assert s12.convert_incoming("STATE", 7) == int(
        DreameVacuumState.SWEEPING_AND_MOPPING
    )
    assert family.convert_incoming("STATE", 8) == int(DreameVacuumState.UPGRADING)
    alarm = next(item for item in family.controls if item.key == "xiaomi_alarm")
    s12_alarm = next(item for item in s12.controls if item.key == "xiaomi_alarm")
    shared = next(item for item in SWEEP_CONTROLS if item.key == "xiaomi_alarm")
    assert alarm == shared
    assert alarm.value_kind is ValueKind.ENUM
    assert s12_alarm.value_kind is ValueKind.BOOL
    assert {item.key for item in family.controls} == {item.key for item in s12.controls}
    assert "CLEANING_MODE" not in family.property_overrides
    assert "SUCTION_LEVEL" not in family.property_overrides
    assert "DND" not in family.property_overrides
    assert "MAP_DATA" not in family.property_overrides
    assert "CHARGING_STATUS" not in family.property_overrides


def test_the_two_brush_services_are_identical() -> None:
    """Siid 14 and 15 publish the same brush life, so neither is mapped."""
    left = comparable_spec_item(_service("c104.json", 14), ("c104",))
    right = comparable_spec_item(_service("c104.json", 15), ("c104",))
    assert isinstance(left, dict)
    assert isinstance(right, dict)
    left.pop("iid", None)
    right.pop("iid", None)
    assert left == right


def test_every_published_status_wire_has_a_shell_state() -> None:
    """The state table covers the status value list and no extra wire."""
    listed = spec_index("c104.json")[("property", 2, 1)].get("value-list")
    assert isinstance(listed, list)
    wires = [item["value"] for item in listed if isinstance(item, dict)]
    assert wires == [*range(9)]
    assert set(wires) == set(SWEEP_STATE_AFTER_READ)


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
    """Each control's options, range, and access follow the released spec."""
    assert_controls_match_spec(_CASE)


def test_every_control_value_is_read_or_sent(socket_enabled: None) -> None:
    """Read every spec sample and send every writable value."""
    del socket_enabled
    exercise_control_values(_CASE)


def test_rejected_control_traffic_is_not_stored(socket_enabled: None) -> None:
    """A refused read or write leaves the stored value unchanged."""
    del socket_enabled
    exercise_rejected_control_traffic(_CASE)

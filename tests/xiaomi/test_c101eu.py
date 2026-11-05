"""Spec coverage for xiaomi.vacuum.c101eu, the Xiaomi Robot Vacuum X20."""

from __future__ import annotations

from custom_components.dreame_vacuum.dreame.types import DreameVacuumState
from custom_components.dreame_vacuum.xiaomi import MODEL_E10, MODEL_S20, MODEL_X20
from custom_components.dreame_vacuum.xiaomi.controls import ValueKind
from custom_components.dreame_vacuum.xiaomi.profile import STATION_PROPERTIES
from custom_components.dreame_vacuum.xiaomi.sweep import SWEEP_CONTROLS, SWEEP_STATES
import pytest
from tests.xiaomi.spec_helpers import (
    X20_ACTION_REASONS as _ACTION_REASONS,
    X20_PROPERTY_REASONS as _PROPERTY_REASONS,
    X20_STATE_AFTER_READ as _STATE_AFTER_READ,
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
    load_spec_document,
    require_family,
    spec_index,
    spec_items,
)

_CASE = SpecCase(
    model=MODEL_X20,
    device_name="Robot Vacuum X20",
    spec_filename="c101eu.json",
    property_reasons=_PROPERTY_REASONS,
    action_reasons=_ACTION_REASONS,
    state_after_read=_STATE_AFTER_READ,
    classification_counts={"c101eu.json": (52, 172)},
    spec_type="urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-c101eu:2",
    reason_prefix_counts={
        "identity": 5,
        "map": 68,
        "needs council": 76,
        "no ha meaning": 24,
    },
    checked_events=((3, 1), (7, 7), (7, 8), (7, 9)),
    state_wire_eight=int(DreameVacuumState.UPGRADING),
    station_shell=False,
    action_spec_filenames=("c101eu.json",),
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


def test_the_published_spec_is_fully_classified() -> None:
    """Every released spec item is mapped or has one explicit omission reason.

    miot-spec.org lists released versions 1 and 2. Version 2 is the latest.
    There is no preview.
    """
    assert_spec_is_fully_classified(_CASE)


def test_released_addresses_overlap_the_sweep_profile() -> None:
    """X20 shares the sweep service layout and not the station layout."""
    x20 = _addresses("c101eu.json")
    sweep = _addresses("b112.json")
    station = _addresses("d109gl.json")
    assert len(x20 & sweep) / len(x20 | sweep) > 0.70
    assert len(x20 & station) / len(x20 | station) < 0.25
    x20_status = spec_index("c101eu.json")[("property", 2, 1)]["value-list"]
    sweep_status = spec_index("b112.json")[("property", 2, 1)]["value-list"]
    assert isinstance(x20_status, list)
    assert isinstance(sweep_status, list)
    assert x20_status[:9] == sweep_status
    assert x20_status != sweep_status


def test_the_record_keeps_sweep_addresses_and_replaces_value_lists() -> None:
    """Shared addresses stay. Status, options, alarm, and reset values differ."""
    family = require_family(MODEL_X20)
    e10 = require_family(MODEL_E10)
    s20 = require_family(MODEL_S20)
    assert family.property_overrides == e10.property_overrides
    assert family.action_overrides == e10.action_overrides
    assert family.property_overrides == s20.property_overrides
    assert family.property_overrides != STATION_PROPERTIES
    assert family.state_by_wire != SWEEP_STATES
    assert family.state_by_wire != s20.state_by_wire
    assert family.convert_incoming("STATE", 8) == int(DreameVacuumState.UPGRADING)
    assert family.convert_incoming("STATE", 9) == int(DreameVacuumState.WASHING)
    assert family.convert_incoming("STATE", 10) == int(DreameVacuumState.DRYING)
    assert family.convert_incoming("STATE", 12) == int(DreameVacuumState.PAUSED)
    assert s20.convert_incoming("STATE", 9) == int(DreameVacuumState.BUILDING)
    assert "CLEANING_MODE" not in family.property_overrides
    assert "SUCTION_LEVEL" not in family.property_overrides
    assert "DND" not in family.property_overrides
    assert "MAP_DATA" not in family.property_overrides
    assert "VOLUME" not in family.property_overrides
    assert "CHARGING_STATUS" not in family.property_overrides
    shared_suction = next(
        item for item in SWEEP_CONTROLS if item.key == "xiaomi_suction"
    )
    assert [value for value, _slug in shared_suction.options] == [0, 1, 2, 3, 4]
    suction = next(item for item in family.controls if item.key == "xiaomi_suction")
    assert [value for value, _slug in suction.options] == [0, 1, 2, 3]
    alarm = next(item for item in family.controls if item.key == "xiaomi_alarm")
    assert alarm.value_kind is ValueKind.BOOL
    reset_filter = next(
        item for item in family.controls if item.key == "xiaomi_reset_filter"
    )
    reset_mop = next(item for item in family.controls if item.key == "xiaomi_reset_mop")
    assert reset_filter.action_parameters == ((17, 3),)
    assert reset_mop.action_parameters == ((17, 4),)
    air_dry = next(item for item in family.controls if item.key == "xiaomi_air_dry")
    assert (air_dry.siid, air_dry.piid) == (7, 54)
    assert not any(item.key == "xiaomi_suction_level" for item in family.controls)
    assert not any(item.siid == 2 and item.piid == 11 for item in family.controls)


def test_every_published_status_wire_has_a_shell_state() -> None:
    """The state table covers the status value list and no extra wire."""
    listed = spec_index("c101eu.json")[("property", 2, 1)].get("value-list")
    assert isinstance(listed, list)
    wires = [item["value"] for item in listed if isinstance(item, dict)]
    assert wires == [*range(13)]
    assert set(wires) == set(_STATE_AFTER_READ)
    document = load_spec_document("c101eu.json")
    assert document["type"] == "urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-c101eu:2"


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

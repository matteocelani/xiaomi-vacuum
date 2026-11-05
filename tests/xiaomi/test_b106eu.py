"""Spec coverage for xiaomi.vacuum.b106eu and the identical T12 alias."""

from __future__ import annotations

from custom_components.dreame_vacuum.dreame.types import DreameVacuumState
from custom_components.dreame_vacuum.xiaomi import (
    MODEL_E10,
    MODEL_S12,
    MODEL_S20,
    MODEL_T12,
)
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
    exercise_control_values,
    exercise_mapped_actions,
    exercise_mapped_property_reads,
    exercise_rejected_control_traffic,
    exercise_status_wires,
    exercise_writable_values,
    load_spec_document,
    normalize_spec,
    require_family,
    spec_index,
    spec_items,
)

_DROPPED_PROPERTY_REASONS = {(7, 48), (7, 49)}
_DROPPED_ACTION_REASONS = {(14, 3), (14, 4)}
_PROPERTY_REASONS = {
    key: reason
    for key, reason in SWEEP_PROPERTY_REASONS.items()
    if key not in _DROPPED_PROPERTY_REASONS
}
_PROPERTY_REASONS.update(
    {
        (2, 9): "map: restricted walls stay unmapped until map support.",
        (2, 10): "map: room ids stay unmapped until map support.",
        (7, 38): "no ha meaning: clean preference type is an action parameter.",
        (7, 39): "no ha meaning: clean preference switch is an action parameter.",
        (7, 40): "no ha meaning: clean preference is neither readable nor writable.",
        (7, 41): "no ha meaning: clean preference switch is an action parameter.",
        (7, 46): "no ha meaning: the sd flag is neither readable nor writable.",
        (7, 55): "map: map encryption stays unmapped until map support.",
        (8, 20): "no ha meaning: current order count is neither readable nor writable.",
    }
)
_ACTION_REASONS = {
    key: reason
    for key, reason in SWEEP_ACTION_REASONS.items()
    if key not in _DROPPED_ACTION_REASONS
}
_ACTION_REASONS.update(
    {
        (2, 7): "map: room sweep takes a room-id parameter.",
        (7, 4): "needs council: setting a clean preference takes an opaque parameter.",
        (7, 5): "needs council: reading a clean preference takes an opaque parameter.",
        (7, 6): "needs council: setting a preference type takes an opaque parameter.",
        (7, 8): "needs council: erasing a preference takes an opaque parameter.",
        (7, 9): "needs council: setting a clean preference takes an opaque parameter.",
        (7, 10): "needs council: reading a clean preference takes an opaque parameter.",
        (8, 6): "needs council: adding a schedule takes an order blob.",
        (9, 9): "map: point clean stays unmapped until map support.",
    }
)
_STATE_AFTER_READ = {
    **SWEEP_STATE_AFTER_READ,
    6: DreameVacuumState.MOPPING,
    7: DreameVacuumState.SWEEPING_AND_MOPPING,
}
_REASON_PREFIX_COUNTS = {
    "identity": 5,
    "map": 66,
    "needs council": 54,
    "no ha meaning": 23,
}


def _case(model: str, filename: str, spec_type: str) -> SpecCase:
    """Build the shared S12 omission case for one released model code."""
    return SpecCase(
        model=model,
        device_name="Robot Vacuum S12" if model == MODEL_S12 else "Robot Vacuum T12",
        spec_filename=filename,
        property_reasons=_PROPERTY_REASONS,
        action_reasons=_ACTION_REASONS,
        state_after_read=_STATE_AFTER_READ,
        classification_counts={filename: (44, 147)},
        spec_type=spec_type,
        reason_prefix_counts=_REASON_PREFIX_COUNTS,
        state_wire_eight=int(DreameVacuumState.UPGRADING),
        station_shell=False,
        action_spec_filenames=(filename,),
    )


_CASES = (
    _case(
        MODEL_S12,
        "b106eu.json",
        "urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-b106eu:1",
    ),
    _case(
        MODEL_T12,
        "b106bk.json",
        "urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-b106bk:1",
    ),
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


@pytest.mark.parametrize("case", _CASES, ids=("b106eu", "b106bk"))
def test_the_published_spec_is_fully_classified(case: SpecCase) -> None:
    """Every released spec item is mapped or has one explicit omission reason.

    miot-spec.org lists released version 1 for both models. b106eu also has
    debug version 2, which this fixture does not use.
    """
    assert_spec_is_fully_classified(case)


def test_released_t12_matches_released_s12() -> None:
    """The two released documents differ only by the model code in the URNs."""
    s12 = normalize_spec(load_spec_document("b106eu.json"), ("b106eu",))
    t12 = normalize_spec(load_spec_document("b106bk.json"), ("b106bk",))
    assert s12 == t12
    assert load_spec_document("b106eu.json")["type"].endswith(":1")
    assert load_spec_document("b106bk.json")["type"].endswith(":1")


def test_t12_reuses_the_s12_record() -> None:
    """T12 is the same codec with its own model code, not a second table."""
    s12 = require_family(MODEL_S12)
    t12 = require_family(MODEL_T12)
    assert s12.model == MODEL_S12
    assert t12.model == MODEL_T12
    assert t12.property_overrides is s12.property_overrides
    assert t12.action_overrides is s12.action_overrides
    assert t12.state_by_wire is s12.state_by_wire
    assert t12.controls is s12.controls
    assert t12.task_by_wire is s12.task_by_wire


def test_released_addresses_overlap_the_sweep_profile() -> None:
    """S12 shares the sweep service layout and not the station layout."""
    s12 = _addresses("b106eu.json")
    t12 = _addresses("b106bk.json")
    sweep = _addresses("b112.json")
    station = _addresses("d109gl.json")
    s20 = _addresses("d106gl.json")
    assert t12 == s12
    assert len(s12 & sweep) / len(s12 | sweep) > 0.70
    assert len(s12 & station) / len(s12 | station) < 0.25
    assert len(s12 & s20) / len(s12 | s20) > 0.70
    s12_status = spec_index("b106eu.json")[("property", 2, 1)]["value-list"]
    sweep_status = spec_index("b112.json")[("property", 2, 1)]["value-list"]
    s20_status = spec_index("d106gl.json")[("property", 2, 1)]["value-list"]
    assert isinstance(s12_status, list)
    assert isinstance(sweep_status, list)
    assert isinstance(s20_status, list)
    assert s12_status[:6] == sweep_status[:6]
    assert s12_status[6]["description"] == "Mopping"
    assert s12_status[7]["description"] == "Sweeping and Mopping"
    assert s12_status != sweep_status
    assert s12_status != s20_status


def test_the_record_keeps_sweep_addresses_and_replaces_value_lists() -> None:
    """Shared addresses stay. Status, options, alarm, and reset values differ."""
    family = require_family(MODEL_S12)
    e10 = require_family(MODEL_E10)
    s20 = require_family(MODEL_S20)
    assert family.property_overrides == e10.property_overrides
    assert family.action_overrides == e10.action_overrides
    assert family.property_overrides != STATION_PROPERTIES
    assert family.state_by_wire != SWEEP_STATES
    assert family.state_by_wire != s20.state_by_wire
    assert family.convert_incoming("STATE", 6) == int(DreameVacuumState.MOPPING)
    assert family.convert_incoming("STATE", 7) == int(
        DreameVacuumState.SWEEPING_AND_MOPPING
    )
    assert family.convert_incoming("STATE", 8) == int(DreameVacuumState.UPGRADING)
    assert "CLEANING_MODE" not in family.property_overrides
    assert "SUCTION_LEVEL" not in family.property_overrides
    assert "DND" not in family.property_overrides
    assert "MAP_DATA" not in family.property_overrides
    assert "VOLUME" not in family.property_overrides
    mode = next(item for item in family.controls if item.key == "xiaomi_sweep_mode")
    s20_mode = next(item for item in s20.controls if item.key == "xiaomi_sweep_mode")
    assert [value for value, _slug in mode.options] == [0, 1, 2]
    assert [value for value, _slug in s20_mode.options] == [0, 1, 2, 3]
    suction = next(item for item in family.controls if item.key == "xiaomi_suction")
    shared_suction = next(
        item for item in SWEEP_CONTROLS if item.key == "xiaomi_suction"
    )
    assert [value for value, _slug in shared_suction.options] == [0, 1, 2, 3, 4]
    assert [value for value, _slug in suction.options] == [0, 1, 2, 3]
    alarm = next(item for item in family.controls if item.key == "xiaomi_alarm")
    assert alarm.value_kind is ValueKind.BOOL
    reset_filter = next(
        item for item in family.controls if item.key == "xiaomi_reset_filter"
    )
    reset_mop = next(item for item in family.controls if item.key == "xiaomi_reset_mop")
    assert reset_filter.action_parameters == ((17, 3),)
    assert reset_mop.action_parameters == ((17, 4),)
    keys = {item.key for item in family.controls}
    assert "xiaomi_suction_level" not in keys
    assert "xiaomi_electrolysis" not in keys
    assert "xiaomi_air_dry" not in keys


@pytest.mark.parametrize("case", _CASES, ids=("b106eu", "b106bk"))
def test_every_published_status_wire_has_a_shell_state(case: SpecCase) -> None:
    """The state table covers the status value list and no extra wire."""
    listed = spec_index(case.spec_filename)[("property", 2, 1)].get("value-list")
    assert isinstance(listed, list)
    wires = [item["value"] for item in listed if isinstance(item, dict)]
    assert wires == [*range(9)]
    assert set(wires) == set(_STATE_AFTER_READ)


@pytest.mark.parametrize("case", _CASES, ids=("b106eu", "b106bk"))
def test_every_control_has_an_english_name(case: SpecCase) -> None:
    """Each control key and option slug has an English translation."""
    assert_controls_have_english_names(case)


@pytest.mark.parametrize("case", _CASES, ids=("b106eu", "b106bk"))
def test_every_mapped_property_reads_each_spec_value(
    case: SpecCase, socket_enabled: None
) -> None:
    del socket_enabled
    exercise_mapped_property_reads(case)


@pytest.mark.parametrize("case", _CASES, ids=("b106eu", "b106bk"))
def test_every_writable_value_is_sent_and_unmapped_writes_are_not(
    case: SpecCase, socket_enabled: None
) -> None:
    del socket_enabled
    exercise_writable_values(case)


@pytest.mark.parametrize("case", _CASES, ids=("b106eu", "b106bk"))
def test_every_mapped_action_is_invoked_or_refused_without_parameters(
    case: SpecCase, socket_enabled: None
) -> None:
    del socket_enabled
    exercise_mapped_actions(case)


@pytest.mark.parametrize("case", _CASES, ids=("b106eu", "b106bk"))
def test_every_status_wire_reaches_the_shell_state(
    case: SpecCase, socket_enabled: None
) -> None:
    del socket_enabled
    exercise_status_wires(case)


@pytest.mark.parametrize("case", _CASES, ids=("b106eu", "b106bk"))
def test_controls_match_the_spec(case: SpecCase) -> None:
    """Each control's options, range, and access follow the released spec."""
    assert_controls_match_spec(case)


@pytest.mark.parametrize("case", _CASES, ids=("b106eu", "b106bk"))
def test_every_control_value_is_read_or_sent(
    case: SpecCase, socket_enabled: None
) -> None:
    """Read every spec sample and send every writable value."""
    del socket_enabled
    exercise_control_values(case)


@pytest.mark.parametrize("case", _CASES, ids=("b106eu", "b106bk"))
def test_rejected_control_traffic_is_not_stored(
    case: SpecCase, socket_enabled: None
) -> None:
    """A refused read or write leaves the stored value unchanged."""
    del socket_enabled
    exercise_rejected_control_traffic(case)

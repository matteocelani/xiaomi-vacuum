"""Spec coverage for xiaomi.vacuum.c108, the Xiaomi Robot Vacuum E5."""

from __future__ import annotations

import json
from pathlib import Path

from custom_components.dreame_vacuum.dreame.types import DreameVacuumState
from custom_components.dreame_vacuum.xiaomi import MODEL_E5
from custom_components.dreame_vacuum.xiaomi.profile import (
    STATION_PROPERTIES,
    STATION_STATES,
)
from custom_components.dreame_vacuum.xiaomi.sweep import SWEEP_PROPERTIES, SWEEP_STATES
import pytest
from tests.xiaomi.spec_helpers import (
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

_PROPERTY_REASONS = {
    (2, 3): "no ha meaning: common params are neither readable nor writable.",
    (2, 11): "needs council: schedule editing takes an order blob.",
    (9, 5): "needs council: the clean record is an opaque string.",
    (10, 2): "needs council: DND time is one packed string, not a start and end.",
    (13, 1): "needs council: remote direction is a momentary command, not a setting.",
    (15, 1): "needs council: timezone offset is not the Dreame timezone property.",
}
_ACTION_REASONS = {
    (2, 5): "needs council: adding a schedule takes an order blob.",
    (2, 6): "needs council: deleting a schedule takes an order blob.",
    (2, 7): "needs council: modifying a schedule takes an order blob.",
}
_STATE_AFTER_READ = {
    1: DreameVacuumState.IDLE,
    2: DreameVacuumState.SWEEPING,
    3: DreameVacuumState.PAUSED,
    4: DreameVacuumState.ERROR,
    5: DreameVacuumState.CHARGING,
    6: DreameVacuumState.RETURNING,
    7: DreameVacuumState.CHARGING_COMPLETED,
}
_CASE = SpecCase(
    model=MODEL_E5,
    device_name="Robot Vacuum E5",
    spec_filename="c108.json",
    property_reasons=_PROPERTY_REASONS,
    action_reasons=_ACTION_REASONS,
    state_after_read=_STATE_AFTER_READ,
    classification_counts={"c108.json": (30, 15)},
    spec_type="urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-c108:1",
    reason_prefix_counts={
        "identity": 5,
        "needs council": 9,
        "no ha meaning": 1,
    },
    checked_events=((3, 1),),
    # Siid 10 is do-not-disturb here. The shared table treats siid 10 as the map.
    service_reasons={
        1: "identity: manufacturer, model, and firmware come from miIO.info.",
    },
    state_wire_eight=-1,
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


def test_the_published_spec_is_fully_classified() -> None:
    """Every released spec item is mapped or has one explicit omission reason.

    miot-spec.org lists a single released version. There is no preview or debug.
    """
    assert_spec_is_fully_classified(_CASE)


def test_released_addresses_overlap_neither_profile() -> None:
    """E5 shares too little, and the shared lists mean different things."""
    e5 = _addresses("c108.json")
    sweep = _addresses("b112.json")
    station = _addresses("d109gl.json")
    assert len(e5 & sweep) / len(e5 | sweep) < 0.25
    assert len(e5 & station) / len(e5 | station) < 0.30
    e5_status = spec_index("c108.json")[("property", 2, 1)]["value-list"]
    sweep_status = spec_index("b112.json")[("property", 2, 1)]["value-list"]
    station_status = spec_index("d109gl.json")[("property", 2, 2)]["value-list"]
    assert e5_status != sweep_status
    assert e5_status != station_status
    assert (
        spec_index("c108.json")[("property", 3, 2)]["value-list"]
        != spec_index("d109gl.json")[("property", 3, 2)]["value-list"]
    )


def test_the_record_does_not_install_either_profile() -> None:
    """The model declares its own maps. It does not compose sweep or station."""
    family = require_family(MODEL_E5)
    assert family.property_overrides != SWEEP_PROPERTIES
    assert family.state_by_wire != SWEEP_STATES
    assert family.property_overrides != STATION_PROPERTIES
    assert family.state_by_wire != STATION_STATES
    assert "CLEANING_MODE" not in family.property_overrides
    assert "SUCTION_LEVEL" not in family.property_overrides
    assert "CHARGING_STATUS" not in family.property_overrides
    assert "DND" not in family.property_overrides
    assert "CLEANING_TIME" not in family.property_overrides
    assert "CLEANED_AREA" not in family.property_overrides
    assert "MAP_DATA" not in family.property_overrides
    assert any(control.siid == 2 and control.piid == 4 for control in family.controls)


def test_every_published_status_wire_has_a_shell_state() -> None:
    """The state table covers the status value list and no extra wire."""
    listed = spec_index("c108.json")[("property", 2, 1)].get("value-list")
    assert isinstance(listed, list)
    wires = [item["value"] for item in listed if isinstance(item, dict)]
    assert wires == [1, 2, 3, 4, 5, 6, 7]
    assert set(wires) == set(_STATE_AFTER_READ)


def test_charging_value_one_is_not_charging() -> None:
    """E5 wire 1 means not charging, so it is not the Dreame charging property."""
    listed = spec_index("c108.json")[("property", 3, 2)].get("value-list")
    assert isinstance(listed, list)
    by_value = {
        item["value"]: item["description"] for item in listed if isinstance(item, dict)
    }
    assert by_value[1] == "Not Charging"
    assert by_value[2] == "Charging"
    assert by_value[3] == "Charging Finish"
    document = load_spec_document("c108.json")
    assert document["type"] == "urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-c108:1"


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


def test_fault_names_follow_the_spec_value_list() -> None:
    """Each c108 fault code uses the description published on that value."""
    family = require_family(MODEL_E5)
    spec = spec_index("c108.json")[("property", 2, 2)]
    listed = spec["value-list"]
    assert isinstance(listed, list)
    strings = json.loads(
        Path("custom_components/dreame_vacuum/strings.json").read_text(encoding="utf-8")
    )
    entity = strings["entity"]
    assert isinstance(entity, dict)
    sensor = entity["sensor"]
    assert isinstance(sensor, dict)
    error = sensor["error"]
    assert isinstance(error, dict)
    states = error["state"]
    assert isinstance(states, dict)
    seen: set[int] = set()
    for item in listed:
        assert isinstance(item, dict)
        code = item["value"]
        description = item["description"]
        assert isinstance(code, int)
        assert isinstance(description, str)
        key = family.fault_name(code)
        assert isinstance(key, str)
        assert key != "unknown"
        assert states[key] == description
        seen.add(code)
    assert family.fault_name(max(seen) + 1) == "unknown"

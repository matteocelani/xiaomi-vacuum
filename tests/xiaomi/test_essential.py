"""Spec coverage for the Essential family: mijia.vacuum.v1, v2, and v3."""

from __future__ import annotations

import json
from pathlib import Path

from custom_components.dreame_vacuum.dreame.const import ERROR_CODE_TO_ERROR_NAME
from custom_components.dreame_vacuum.dreame.types import (
    DreameVacuumProperty,
    DreameVacuumState,
)
from custom_components.dreame_vacuum.xiaomi import (
    MODEL_E10,
    MODEL_MIJIA_ESSENTIAL,
    MODEL_MIJIA_ESSENTIAL_V3,
    MODEL_MIJIA_G1,
)
from custom_components.dreame_vacuum.xiaomi.profile import (
    STATION_PROPERTIES,
    STATION_STATES,
)
from custom_components.dreame_vacuum.xiaomi.sweep import SWEEP_PROPERTIES, SWEEP_STATES
import pytest
from tests.xiaomi.helpers import FakeMiio, release_device
from tests.xiaomi.spec_helpers import (
    SpecCase,
    assert_controls_have_english_names,
    assert_controls_match_spec,
    assert_spec_is_fully_classified,
    connect_device,
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
    (7, 1): "map: map points stay unmapped until map support.",
    (8, 1): "needs council: remote direction is a momentary command, not a setting.",
    (9, 6): "no ha meaning: the clean record is neither readable nor writable.",
    (16, 1): "needs council: mop status values are unnamed.",
    (16, 2): "no ha meaning: log text is neither readable nor writable.",
}
_STATE_AFTER_READ = {
    1: DreameVacuumState.IDLE,
    2: DreameVacuumState.SWEEPING,
    3: DreameVacuumState.PAUSED,
    4: DreameVacuumState.ERROR,
    5: DreameVacuumState.CHARGING,
    6: DreameVacuumState.RETURNING,
}
_COUNTS = (31, 13)
_PREFIXES = {
    "identity": 4,
    "map": 1,
    "needs council": 6,
    "no ha meaning": 2,
}
_CASES = (
    SpecCase(
        model=MODEL_MIJIA_G1,
        device_name="Mijia G1",
        spec_filename="v1.json",
        property_reasons=_PROPERTY_REASONS,
        action_reasons={},
        state_after_read=_STATE_AFTER_READ,
        classification_counts={"v1.json": _COUNTS},
        spec_type="urn:miot-spec-v2:device:vacuum:0000A006:mijia-v1:1",
        reason_prefix_counts=_PREFIXES,
        checked_events=((7, 1), (7, 2), (9, 1), (16, 1)),
        state_wire_eight=8,
        station_shell=False,
        required_service_ids=(1,),
    ),
    SpecCase(
        model=MODEL_MIJIA_ESSENTIAL,
        device_name="Robot Vacuum-Mop Essential",
        spec_filename="v2.json",
        property_reasons=_PROPERTY_REASONS,
        action_reasons={},
        state_after_read=_STATE_AFTER_READ,
        classification_counts={"v2.json": _COUNTS},
        spec_type="urn:miot-spec-v2:device:vacuum:0000A006:mijia-v2:1",
        reason_prefix_counts=_PREFIXES,
        checked_events=((7, 1), (7, 2), (9, 1), (16, 1)),
        state_wire_eight=8,
        station_shell=False,
        required_service_ids=(1,),
    ),
    SpecCase(
        model=MODEL_MIJIA_ESSENTIAL_V3,
        device_name="Robot Vacuum-Mop Essential v3",
        spec_filename="v3.json",
        property_reasons=_PROPERTY_REASONS,
        action_reasons={},
        state_after_read=_STATE_AFTER_READ,
        classification_counts={"v3.json": _COUNTS},
        spec_type="urn:miot-spec-v2:device:vacuum:0000A006:mijia-v3:1",
        reason_prefix_counts=_PREFIXES,
        checked_events=((7, 1), (7, 2), (9, 1), (16, 1)),
        state_wire_eight=8,
        station_shell=False,
        required_service_ids=(1,),
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


@pytest.mark.parametrize("case", _CASES, ids=("v1", "v2", "v3"))
def test_the_published_spec_is_fully_classified(case: SpecCase) -> None:
    """Each released spec item is mapped or has one explicit omission reason.

    miot-spec.org lists released version 1 and debug version 2. The fixture
    is released version 1.
    """
    assert_spec_is_fully_classified(case)


def test_released_addresses_overlap_neither_profile() -> None:
    """Essential shares too little, and the shared lists mean different things."""
    essential = _addresses("v1.json")
    sweep = _addresses("b112.json")
    station = _addresses("d109gl.json")
    e5 = _addresses("c108.json")
    assert len(essential & sweep) / len(essential | sweep) < 0.20
    assert len(essential & station) / len(essential | station) < 0.20
    essential_status = spec_index("v1.json")[("property", 2, 1)]["value-list"]
    assert essential_status != spec_index("b112.json")[("property", 2, 1)]["value-list"]
    assert (
        essential_status != spec_index("d109gl.json")[("property", 2, 2)]["value-list"]
    )
    assert (
        spec_index("v1.json")[("action", 2, 3)]["description"]
        != spec_index("b112.json")[("action", 2, 3)]["description"]
    )
    assert (
        spec_index("v1.json")[("action", 2, 3)]["description"]
        != spec_index("c108.json")[("action", 2, 3)]["description"]
    )
    assert (
        spec_index("v1.json")[("property", 3, 2)]["value-list"]
        != spec_index("c108.json")[("property", 3, 2)]["value-list"]
    )
    assert (
        spec_index("v1.json")[("property", 2, 5)]["value-list"]
        != spec_index("c108.json")[("property", 2, 5)]["value-list"]
    )
    assert len(essential & e5) / len(essential | e5) < 0.50


@pytest.mark.parametrize("case", _CASES, ids=("v1", "v2", "v3"))
def test_every_published_status_wire_has_a_shell_state(case: SpecCase) -> None:
    """The state table covers the status value list and no extra wire."""
    listed = spec_index(case.spec_filename)[("property", 2, 1)].get("value-list")
    assert isinstance(listed, list)
    wires = [item["value"] for item in listed if isinstance(item, dict)]
    assert wires == [1, 2, 3, 4, 5, 6]
    assert set(wires) == set(case.state_after_read)


def test_charging_value_zero_is_not_charging() -> None:
    """Wire 0 means not charging, so it is not the Dreame charging property."""
    for filename in ("v1.json", "v2.json", "v3.json"):
        listed = spec_index(filename)[("property", 3, 2)].get("value-list")
        assert isinstance(listed, list)
        by_value = {
            item["value"]: item["description"]
            for item in listed
            if isinstance(item, dict)
        }
        assert by_value[0] in {"Not-charging", "Not charging"}
        assert by_value[1] == "Charging"
        assert by_value[2] == "Charging-competely"


def test_the_three_records_share_the_essential_profile() -> None:
    """v2 changes voice language. v3 also moves Start Charge."""
    first = require_family(MODEL_MIJIA_G1)
    second = require_family(MODEL_MIJIA_ESSENTIAL)
    third = require_family(MODEL_MIJIA_ESSENTIAL_V3)
    assert first.property_overrides != SWEEP_PROPERTIES
    assert first.state_by_wire != SWEEP_STATES
    assert first.property_overrides != STATION_PROPERTIES
    assert first.state_by_wire != STATION_STATES
    assert second.property_overrides == first.property_overrides
    assert third.property_overrides == first.property_overrides
    assert second.action_overrides == first.action_overrides
    assert third.action_overrides["CHARGE"] == {"siid": 3, "aiid": 1}
    assert first.action_overrides["CHARGE"] == {"siid": 2, "aiid": 3}
    assert "CHARGING_STATUS" not in first.property_overrides
    assert "CLEANING_MODE" not in first.property_overrides
    assert "SUCTION_LEVEL" not in first.property_overrides
    assert "MAP_DATA" not in first.property_overrides
    assert "DND" in first.property_overrides
    assert "VOLUME" in first.property_overrides
    first_language = next(
        item for item in first.controls if item.key == "xiaomi_voice_language"
    )
    second_language = next(
        item for item in second.controls if item.key == "xiaomi_voice_language"
    )
    third_language = next(
        item for item in third.controls if item.key == "xiaomi_voice_language"
    )
    assert [value for value, _slug in first_language.options] == [0, 1]
    assert [value for value, _slug in second_language.options] == list(range(9))
    assert first_language.options != second_language.options
    assert first_language.options != third_language.options
    assert [item.key for item in second.controls] == [
        item.key for item in first.controls
    ]
    assert [item.key for item in third.controls] == [
        item.key for item in first.controls
    ]


_UNLISTED_FAULTS: tuple[int, ...] = (13, 99)
_STRINGS = Path("custom_components/dreame_vacuum/strings.json")


def test_every_fault_code_uses_the_spec_name_not_a_dreame_name(
    socket_enabled: None,
) -> None:
    """Each published fault code shows that spec's description, never a Dreame name.

    A code the value list does not describe stays unknown.
    """
    del socket_enabled
    document = json.loads(_STRINGS.read_text(encoding="utf-8"))
    sensor = document["entity"]["sensor"]["error"]
    state_names = sensor["state"]
    descriptions = sensor["state_attributes"]["description"]["state"]
    dreame_names = set(ERROR_CODE_TO_ERROR_NAME.values())
    assert require_family(MODEL_E10).fault_name(1) is None
    for case in _CASES:
        listed = spec_index(case.spec_filename)[("property", 2, 2)].get("value-list")
        assert isinstance(listed, list)
        published = {
            item["value"]: item["description"]
            for item in listed
            if isinstance(item, dict)
        }
        family = require_family(case.model)
        error = family.property_overrides["ERROR"]
        with FakeMiio(case.model) as fake:
            device = connect_device(case.device_name + " Fault")
            try:
                for code, description in published.items():
                    assert description
                    fake.set_value(error["siid"], error["piid"], code)
                    device._request_properties([DreameVacuumProperty.ERROR])
                    name = device.status.error_name
                    assert name not in dreame_names
                    assert state_names[name] == description
                    assert descriptions[name] == description
                for code in _UNLISTED_FAULTS:
                    fake.set_value(error["siid"], error["piid"], code)
                    device._request_properties([DreameVacuumProperty.ERROR])
                    assert device.status.error_name == "unknown"
                    assert device.status.error_name != "no_error"
                    assert device.status.error_name != "side_brush"
                    assert device.status.error_name != "brush"
            finally:
                release_device(device)


def test_released_version_one_is_the_document() -> None:
    """Debug version 2 is not the document these models map."""
    assert (
        load_spec_document("v1.json")["type"]
        == "urn:miot-spec-v2:device:vacuum:0000A006:mijia-v1:1"
    )
    assert (
        load_spec_document("v2.json")["type"]
        == "urn:miot-spec-v2:device:vacuum:0000A006:mijia-v2:1"
    )
    assert (
        load_spec_document("v3.json")["type"]
        == "urn:miot-spec-v2:device:vacuum:0000A006:mijia-v3:1"
    )


@pytest.mark.parametrize("case", _CASES, ids=("v1", "v2", "v3"))
def test_every_control_has_an_english_name(case: SpecCase) -> None:
    """Each control key and option slug has an English translation."""
    assert_controls_have_english_names(case)


@pytest.mark.parametrize("case", _CASES, ids=("v1", "v2", "v3"))
def test_every_mapped_property_reads_each_spec_value(
    case: SpecCase, socket_enabled: None
) -> None:
    del socket_enabled
    exercise_mapped_property_reads(case)


@pytest.mark.parametrize("case", _CASES, ids=("v1", "v2", "v3"))
def test_every_writable_value_is_sent_and_unmapped_writes_are_not(
    case: SpecCase, socket_enabled: None
) -> None:
    del socket_enabled
    exercise_writable_values(case)


@pytest.mark.parametrize("case", _CASES, ids=("v1", "v2", "v3"))
def test_every_mapped_action_is_invoked_or_refused_without_parameters(
    case: SpecCase, socket_enabled: None
) -> None:
    del socket_enabled
    exercise_mapped_actions(case)


@pytest.mark.parametrize("case", _CASES, ids=("v1", "v2", "v3"))
def test_every_status_wire_reaches_the_shell_state(
    case: SpecCase, socket_enabled: None
) -> None:
    del socket_enabled
    exercise_status_wires(case)


@pytest.mark.parametrize("case", _CASES, ids=("v1", "v2", "v3"))
def test_controls_match_the_spec(case: SpecCase) -> None:
    """Each control's options, range, and access follow the released spec."""
    assert_controls_match_spec(case)


@pytest.mark.parametrize("case", _CASES, ids=("v1", "v2", "v3"))
def test_every_control_value_is_read_or_sent(
    case: SpecCase, socket_enabled: None
) -> None:
    """Read every spec sample and send every writable value."""
    del socket_enabled
    exercise_control_values(case)


@pytest.mark.parametrize("case", _CASES, ids=("v1", "v2", "v3"))
def test_rejected_control_traffic_is_not_stored(
    case: SpecCase, socket_enabled: None
) -> None:
    """A refused read or write leaves the stored value unchanged."""
    del socket_enabled
    exercise_rejected_control_traffic(case)

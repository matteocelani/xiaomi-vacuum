"""Spec coverage for mijia.vacuum.b108za, the Mijia Sweep Mop 2S."""

from __future__ import annotations

from custom_components.dreame_vacuum.dreame.types import (
    DreameVacuumState,
    DreameVacuumTaskStatus,
)
from custom_components.dreame_vacuum.xiaomi import MODEL_MIJIA_SWEEP_MOP_2S
from custom_components.dreame_vacuum.xiaomi.mapping import MODEL_S20_PLUS
import pytest
from tests.xiaomi.spec_helpers import (
    MIJIA_B108_STATE_AFTER_READ,
    SpecCase,
    assert_controls_have_english_names,
    assert_controls_match_spec,
    assert_spec_is_fully_classified,
    exercise_control_values,
    exercise_mapped_actions,
    exercise_mapped_property_reads,
    exercise_status_wires,
    exercise_writable_values,
    mapped_addresses,
    mijia_b108_case,
    require_family,
    spec_index,
)

_CASE: SpecCase = mijia_b108_case(
    MODEL_MIJIA_SWEEP_MOP_2S,
    "Mijia Sweep Mop 2S",
    "b108za.json",
    "urn:miot-spec-v2:device:vacuum:0000A006:mijia-b108za:1",
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
    """The state table covers the status value list and no extra wire."""
    listed = spec_index("b108za.json")[("property", 2, 1)].get("value-list")
    assert isinstance(listed, list)
    wires = [item["value"] for item in listed if isinstance(item, dict)]
    assert set(wires) == set(MIJIA_B108_STATE_AFTER_READ)


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


def test_the_record_is_an_s20_plus_variant_without_carpet_cleaning() -> None:
    """Carpet cleaning is absent. Edge and point are new sweep types. Remote uses the legacy code."""
    current = require_family(MODEL_MIJIA_SWEEP_MOP_2S)
    base = require_family(MODEL_S20_PLUS)
    assert current is not base
    assert current.model != base.model
    assert "CARPET_CLEANING" in base.property_overrides
    assert "CARPET_CLEANING" not in current.property_overrides
    assert (2, 20) not in mapped_addresses(current, "property")
    assert (2, 20) in mapped_addresses(base, "property")
    without_carpet = {
        name: address
        for name, address in base.property_overrides.items()
        if name != "CARPET_CLEANING"
    }
    assert current.property_overrides == without_carpet
    assert current.action_overrides == base.action_overrides
    assert {control.key for control in current.controls} == {
        "xiaomi_alarm",
        "xiaomi_carpet_avoidance",
        "xiaomi_clean_times",
        "xiaomi_fan_mode",
    }
    fan = next(
        control for control in current.controls if control.key == "xiaomi_fan_mode"
    )
    assert fan.options == ((1, "silent"), (2, "basic"), (4, "full_speed"))
    assert current.state_by_wire[7] == int(DreameVacuumState.WATER_CHECK)
    assert current.convert_incoming("STATE", 7) == int(DreameVacuumState.WATER_CHECK)
    assert base.state_by_wire[7] == int(DreameVacuumState.REMOTE_CONTROL)
    shared_states = set(base.state_by_wire) - {7}
    assert {wire: current.state_by_wire[wire] for wire in shared_states} == {
        wire: base.state_by_wire[wire] for wire in shared_states
    }
    assert current.task_by_wire[2] == int(DreameVacuumTaskStatus.ZONE_CLEANING)
    assert current.task_by_wire[3] == int(DreameVacuumTaskStatus.SPOT_CLEANING)
    assert 2 not in base.task_by_wire
    assert 3 not in base.task_by_wire
    shared = set(base.task_by_wire)
    assert {wire: current.task_by_wire[wire] for wire in shared} == base.task_by_wire

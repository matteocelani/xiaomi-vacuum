"""Spec coverage for mijia.vacuum.b108zb, the Mijia Sweep Mop 3S."""

from __future__ import annotations

from custom_components.dreame_vacuum.xiaomi import (
    MODEL_MIJIA_SWEEP_MOP_2S,
    MODEL_MIJIA_SWEEP_MOP_3S,
)
import pytest
from tests.xiaomi.spec_helpers import (
    MIJIA_B108_STATE_AFTER_READ,
    SpecCase,
    assert_controls_have_english_names,
    assert_controls_match_spec,
    assert_spec_is_fully_classified,
    comparable_spec_item,
    exercise_control_values,
    exercise_mapped_actions,
    exercise_mapped_property_reads,
    exercise_status_wires,
    exercise_writable_values,
    mijia_b108_case,
    require_family,
    spec_index,
)

_CASE: SpecCase = mijia_b108_case(
    MODEL_MIJIA_SWEEP_MOP_3S,
    "Mijia Sweep Mop 3S",
    "b108zb.json",
    "urn:miot-spec-v2:device:vacuum:0000A006:mijia-b108zb:1",
)
_CODES = ("mijia-b108za", "mijia-b108zb")

pytestmark = [
    pytest.mark.enable_socket,
    pytest.mark.allow_hosts(["127.0.0.1"]),
]


def test_the_published_spec_is_fully_classified() -> None:
    """Each spec item is mapped or has one explicit omission reason.

    miot-spec.org lists released version 1 and debug version 2. Version 1 is used.
    """
    assert_spec_is_fully_classified(_CASE)


def test_every_published_status_wire_has_a_shell_state() -> None:
    """The state table covers the status value list and no extra wire."""
    listed = spec_index("b108zb.json")[("property", 2, 1)].get("value-list")
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


def test_released_version_1_aliases_the_2s_record() -> None:
    """Debug version 2 is not this record. Released version 1 matches the 2S spec."""
    current = spec_index("b108zb.json")
    base_spec = spec_index("b108za.json")
    assert set(current) == set(base_spec)
    for key in current:
        assert comparable_spec_item(current[key], _CODES) == comparable_spec_item(
            base_spec[key], _CODES
        )
    chinese = require_family(MODEL_MIJIA_SWEEP_MOP_3S)
    base = require_family(MODEL_MIJIA_SWEEP_MOP_2S)
    assert chinese.model != base.model
    assert chinese.property_overrides == base.property_overrides
    assert chinese.action_overrides == base.action_overrides
    assert chinese.state_by_wire == base.state_by_wire
    assert chinese.task_by_wire == base.task_by_wire
    assert chinese.controls == base.controls

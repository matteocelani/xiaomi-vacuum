"""Spec coverage for xiaomi.vacuum.c103, the Mijia 3C."""

from __future__ import annotations

from custom_components.dreame_vacuum.dreame.types import DreameVacuumState
from custom_components.dreame_vacuum.xiaomi import MODEL_MIJIA_3C, MODEL_S20
import pytest
from tests.xiaomi.spec_helpers import (
    S20_ACTION_REASONS,
    S20_PROPERTY_REASONS,
    S20_STATE_AFTER_READ,
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
    require_family,
    spec_index,
    with_reason_overrides,
)

_STATE_AFTER_READ = {
    **S20_STATE_AFTER_READ,
    10: DreameVacuumState.CHARGING_COMPLETED,
}
_CASE = SpecCase(
    model=MODEL_MIJIA_3C,
    device_name="Mijia 3C",
    spec_filename="c103.json",
    property_reasons=with_reason_overrides(
        S20_PROPERTY_REASONS,
        drop=((14, 3), (14, 4), (14, 5), (14, 6)),
    ),
    action_reasons=with_reason_overrides(S20_ACTION_REASONS, drop=((14, 2),)),
    state_after_read=_STATE_AFTER_READ,
    classification_counts={
        "c103.json": (48, 163),
        "c103_v1.json": (48, 161),
    },
    spec_type="urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-c103:2",
    reason_prefix_counts={
        "identity": 10,
        "map": 137,
        "needs council": 143,
        "no ha meaning": 36,
    },
    absent_items=(
        ("action", 14, 2),
        ("property", 10, 24),
        ("property", 14, 3),
        ("property", 14, 4),
        ("property", 14, 5),
        ("property", 14, 6),
    ),
    checked_events=((3, 1), (7, 9)),
    state_wire_eight=int(S20_STATE_AFTER_READ[8]),
    station_shell=False,
    action_spec_filenames=("c103.json", "c103_v1.json"),
    previous_spec_filename="c103_v1.json",
)

pytestmark = [
    pytest.mark.enable_socket,
    pytest.mark.allow_hosts(["127.0.0.1"]),
]


def test_the_published_spec_is_fully_classified() -> None:
    """Each spec item is mapped or has one explicit omission reason.

    miot-spec.org lists released versions 1 and 2. Version 2 is the latest.
    """
    assert_spec_is_fully_classified(_CASE)


def test_every_published_status_wire_has_a_shell_state() -> None:
    """The state table covers the status value list and no extra wire."""
    listed = spec_index("c103.json")[("property", 2, 1)].get("value-list")
    assert isinstance(listed, list)
    wires = [item["value"] for item in listed if isinstance(item, dict)]
    labels = {
        item["value"]: item["description"] for item in listed if isinstance(item, dict)
    }
    assert labels[10] == "Charged"
    assert set(wires) == set(_STATE_AFTER_READ)


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


def test_charged_decodes_without_changing_the_s20_record() -> None:
    """Wire 10 is Charged here and Charging on S20. The S20 record stays put."""
    current = spec_index("c103.json")
    global_spec = spec_index("d106gl.json")
    assert set(current) - set(global_spec) == set()
    assert set(global_spec) - set(current) == {
        ("action", 14, 2),
        ("property", 10, 24),
        ("property", 14, 3),
        ("property", 14, 4),
        ("property", 14, 5),
        ("property", 14, 6),
    }
    chinese = require_family(MODEL_MIJIA_3C)
    base = require_family(MODEL_S20)
    assert chinese.property_overrides == base.property_overrides
    assert chinese.action_overrides == base.action_overrides
    assert chinese.controls == base.controls
    assert chinese.task_by_wire == base.task_by_wire
    assert chinese.convert_incoming("STATE", 10) == int(
        DreameVacuumState.CHARGING_COMPLETED
    )
    assert base.convert_incoming("STATE", 10) == int(DreameVacuumState.CHARGING)
    assert base.state_by_wire[10] == int(DreameVacuumState.CHARGING)

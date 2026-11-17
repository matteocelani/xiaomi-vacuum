"""Spec coverage for xiaomi.vacuum.ov43gb, the Xiaomi Robot Vacuum H50."""

from __future__ import annotations

from typing import Final

from custom_components.xiaomi_robot_vacuum.dreame.types import DreameVacuumState
from custom_components.xiaomi_robot_vacuum.xiaomi import MODEL_H50
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
    normalize_spec,
    spec_index,
)

_PROPERTY_REASONS: Final[dict[tuple[int, int], str]] = {
    (2, 1): "no ha meaning: firmware is already exposed from miIO.info.",
    (2, 12): "map: zone ids.",
    (2, 13): "map: restricted areas.",
    (2, 14): "map: virtual walls.",
    (2, 15): "map: room ids are not readable.",
    (2, 16): "map: room information.",
    (2, 22): "map: carpet display is map rendering.",
    (2, 24): "no ha meaning: common params are neither readable nor writable.",
    (2, 27): "map: map-complete dialog.",
    (2, 39): "no ha meaning: button type is neither readable nor writable.",
    (2, 42): "needs council: user-defined sweep config needs a program editor.",
    (2, 43): "needs council: user-defined sweep id needs a program editor.",
    (2, 53): "needs council: water-check list is an opaque string.",
    (2, 56): "map: AI objects.",
    (2, 57): "map: furniture.",
    (2, 58): "map: carpet objects.",
    (2, 65): "map: vacuum route is not readable and is map geometry.",
    (2, 67): "no ha meaning: action result is a command echo.",
    (2, 70): "needs council: plugin reminder text needs a text entity.",
    (2, 99): "map: sill geometry.",
    (2, 102): "map: automation furniture.",
    (11, 2): "needs council: DND time is one packed integer, not a start and end.",
    (15, 1): "needs council: target voice id encoding is not a Dreame voice property.",
    (15, 5): "no ha meaning: voice url is neither readable nor writable.",
    (15, 6): "no ha meaning: voice common params are neither readable nor writable.",
    (20, 1): "no ha meaning: unnamed field is neither readable nor writable.",
    (20, 2): "no ha meaning: unnamed field is neither readable nor writable.",
    (20, 3): "needs council: unnamed readable string.",
    (17, 1): "no ha meaning: unnamed field is neither readable nor writable.",
    (17, 2): "needs council: unnamed readable string.",
    (21, 1): "map: cruise position is map geometry.",
    (21, 7): "no ha meaning: stream common params are neither readable nor writable.",
    (22, 1): "no ha meaning: self-check items are neither readable nor writable.",
}

_ACTION_REASONS: Final[dict[tuple[int, int], str]] = {
    (2, 10): "map: zone config takes a zone-id parameter.",
    (2, 11): "map: room config takes a room-id parameter.",
    (2, 12): "map: set-zone takes a zone parameter.",
    (2, 13): "map: room clean config takes a room-id parameter.",
    (2, 14): "map: split room is a map edit.",
    (2, 15): "map: merge rooms is a map edit.",
    (2, 16): "map: room sweep takes a room-id parameter.",
    (2, 17): "map: build-map stays unmapped until map support.",
    (2, 23): "needs council: adding a schedule takes an order blob.",
    (2, 24): "needs council: modifying a schedule takes an order blob.",
    (2, 25): "needs council: deleting a schedule takes an order blob.",
    (2, 26): "needs council: remote direction requires a button-type parameter.",
    (2, 30): "no ha meaning: system info is a diagnostic fetch, not a user control.",
    (2, 33): "map: continue build-map stays unmapped until map support.",
    (2, 34): "map: stop build-map stays unmapped until map support.",
    (2, 35): "map: pause build-map stays unmapped until map support.",
    (2, 37): "map: zone sweep takes a zone parameter.",
    (2, 38): "needs council: adding a user sweep takes a config parameter.",
    (2, 39): "needs council: deleting a user sweep takes an id parameter.",
    (2, 40): "needs council: modifying a user sweep takes a config parameter.",
    (2, 41): "needs council: setting a user sweep takes a config parameter.",
    (2, 42): "needs council: starting a user sweep takes an id parameter.",
    (2, 47): "map: the vacuum route takes a parameter and is map geometry.",
    (2, 48): "needs council: closing an abnormal card takes an opaque parameter.",
    (2, 52): "map: skip cleaning takes a room-id parameter.",
    (2, 53): "map: final cleaning takes a room-id parameter.",
    (2, 54): "map: temporary room cleaning takes a room-id parameter.",
    (2, 55): "map: temporary zone cleaning takes a zone parameter.",
    (2, 56): "map: furniture cleaning takes a map parameter.",
    (2, 60): "needs council: operating an AI object takes an opaque parameter.",
    (2, 61): "map: AI picture objects stay unmapped until map support.",
    (2, 62): "needs council: common-object clean takes an object parameter.",
    (15, 1): "needs council: voice download takes a pack url.",
    (15, 2): "no ha meaning: download status is already the mapped property.",
    (20, 1): "map: history objects stay unmapped until map support.",
    (20, 2): "needs council: user-defined info takes an opaque parameter.",
    (20, 3): "map: stopping a map upload stays unmapped until map support.",
    (20, 5): "needs council: reading a schedule takes an opaque parameter.",
    (20, 6): "needs council: switching a schedule takes an opaque parameter.",
    (17, 1): "map: AI pictures stay unmapped until map support.",
    (21, 1): "needs council: auto cruise takes an opaque parameter.",
    (21, 2): "needs council: arriving at a place takes an opaque parameter.",
    (21, 5): "no ha meaning: video status is a diagnostic fetch, not a user control.",
    (
        21,
        6,
    ): "needs council: setting a video password must not be sent as a raw action.",
    (
        21,
        7,
    ): "needs council: verifying a video password must not be sent as a raw action.",
    (
        21,
        8,
    ): "needs council: forgot-password changes a video credential and has no confirmation flow.",
}

_STATE_AFTER_READ: Final[dict[int, DreameVacuumState]] = {
    1: DreameVacuumState.IDLE,
    2: DreameVacuumState.CHARGING,
    3: DreameVacuumState.CHARGING,
    4: DreameVacuumState.SWEEPING,
    5: DreameVacuumState.PAUSED,
    6: DreameVacuumState.RETURNING,
    7: DreameVacuumState.RETURNING_TO_WASH,
    8: DreameVacuumState.REMOTE_CONTROL,
    9: DreameVacuumState.CHARGING_COMPLETED,
    10: DreameVacuumState.BUILDING,
    11: DreameVacuumState.UPGRADING,
    12: DreameVacuumState.STATION_CLEANING,
    13: DreameVacuumState.CHARGING,
    14: DreameVacuumState.STATION_CLEANING,
    15: DreameVacuumState.ERROR,
    16: DreameVacuumState.SWEEPING_AND_MOPPING,
    17: DreameVacuumState.MOPPING,
    18: DreameVacuumState.PAUSED,
    19: DreameVacuumState.RETURNING,
    20: DreameVacuumState.RETURNING_TO_WASH,
    21: DreameVacuumState.BUILDING,
    22: DreameVacuumState.WASHING,
    23: DreameVacuumState.CHARGING_COMPLETED,
    24: DreameVacuumState.RETURNING,
}

_CASE = SpecCase(
    model=MODEL_H50,
    device_name="H50",
    spec_filename="ov43gb.json",
    property_reasons=_PROPERTY_REASONS,
    action_reasons=_ACTION_REASONS,
    state_after_read=_STATE_AFTER_READ,
    classification_counts={
        "ov43gb.json": (156, 118),
        "ov43gb_v1.json": (155, 117),
    },
    spec_type="urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-ov43gb:2",
    reason_prefix_counts={
        "identity": 10,
        "map": 118,
        "needs council": 80,
        "no ha meaning": 27,
    },
    version_only_controls=frozenset({(22, 2)}),
    absent_items=(
        ("property", 20, 9),
        ("property", 20, 11),
    ),
    action_spec_filenames=("ov43gb.json", "ov43gb_v1.json"),
    previous_spec_filename="ov43gb_v1.json",
)

pytestmark = [
    pytest.mark.enable_socket,
    pytest.mark.allow_hosts(["127.0.0.1"]),
]


def test_the_published_spec_is_fully_classified() -> None:
    """Each spec item is mapped or has one explicit omission reason.

    miot-spec.org lists released versions 1 and 2. Version 2 is the latest.
    home.miot-spec.com names xiaomi.vacuum.ov43gb the Xiaomi Robot Vacuum H50.
    """
    assert_spec_is_fully_classified(_CASE)


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


def test_published_spec_matches_vacuum_5_pro_except_drying_and_hardware() -> None:
    """Version 2 drops 5 Pro lidar items and extends drying time through 12 hours."""
    current = spec_index("ov43gb.json")
    vacuum_5_pro = spec_index("ov21gl.json")
    assert set(vacuum_5_pro) - set(current) == {
        ("action", 2, 65),
        ("action", 20, 7),
        ("action", 20, 8),
        ("action", 21, 4),
        ("property", 2, 103),
        ("property", 20, 4),
        ("property", 20, 5),
        ("property", 20, 6),
        ("property", 20, 9),
        ("property", 20, 11),
        ("property", 20, 12),
    }
    assert set(current) - set(vacuum_5_pro) == {
        ("event", 2, 6),
        ("event", 2, 7),
        ("event", 3, 1),
        ("event", 10, 1),
        ("event", 10, 2),
        ("event", 18, 1),
        ("property", 22, 1),
        ("property", 22, 2),
    }
    changed = {
        ("property", 2, 31),
        ("property", 2, 83),
    }
    codes = ("ov43gb", "ov21gl")
    for key in (set(current) & set(vacuum_5_pro)) - changed:
        assert normalize_spec(current[key], codes) == normalize_spec(
            vacuum_5_pro[key], codes
        ), key
    listed = current[("property", 2, 31)].get("value-list")
    assert isinstance(listed, list)
    assert [item["description"] for item in listed if isinstance(item, dict)] == [
        "2 Hours",
        "3 Hours",
        "4 Hours",
        "5 Hours",
        "6 Hours",
        "7 Hours",
        "8 Hours",
        "9 Hours",
        "10 Hours",
        "11 Hours",
        "12 Hours",
    ]
    worry_free = current[("property", 2, 83)].get("value-list")
    assert isinstance(worry_free, list)
    assert [item["description"] for item in worry_free if isinstance(item, dict)] == [
        "Silent Clean",
        "Deep Clean",
        "General",
        "Butler",
        "Pet ",
    ]


def test_published_spec_matches_h50_pro_except_stream_and_drying() -> None:
    """Version 2 adds the stream service and extends drying time through 12 hours."""
    current = spec_index("ov43gb.json")
    h50_pro = spec_index("ov42gl.json")
    assert set(current) - set(h50_pro) == {
        ("action", 21, 1),
        ("action", 21, 2),
        ("action", 21, 3),
        ("action", 21, 5),
        ("action", 21, 6),
        ("action", 21, 7),
        ("action", 21, 8),
        ("property", 21, 1),
        ("property", 21, 2),
        ("property", 21, 3),
        ("property", 21, 4),
        ("property", 21, 5),
        ("property", 21, 6),
        ("property", 21, 7),
        ("property", 21, 8),
    }
    assert set(h50_pro) - set(current) == {
        ("property", 20, 6),
        ("property", 20, 13),
    }
    changed = {
        ("action", 20, 6),
        ("property", 2, 31),
    }
    codes = ("ov43gb", "ov42gl")
    for key in (set(current) & set(h50_pro)) - changed:
        assert normalize_spec(current[key], codes) == normalize_spec(
            h50_pro[key], codes
        ), key
    schedule = ("action", 20, 6)
    current_action = normalize_spec(current[schedule], codes)
    h50_pro_action = normalize_spec(h50_pro[schedule], codes)
    assert isinstance(current_action, dict)
    assert isinstance(h50_pro_action, dict)
    current_fields = dict(current_action)
    h50_pro_fields = dict(h50_pro_action)
    assert current_fields.pop("in") == [1]
    assert h50_pro_fields.pop("in") == [2]
    assert current_fields == h50_pro_fields


def test_version_2_adds_only_self_check() -> None:
    """Released version 2 adds the two self-check properties version 1 omits."""
    current = spec_index("ov43gb.json")
    previous = spec_index("ov43gb_v1.json")
    assert set(current) - set(previous) == {
        ("property", 22, 1),
        ("property", 22, 2),
    }
    assert set(previous) - set(current) == set()
    codes = ("xiaomi-ov43gb:1", "xiaomi-ov43gb:2")
    for key in set(previous):
        assert normalize_spec(current[key], codes) == normalize_spec(
            previous[key], codes
        ), key

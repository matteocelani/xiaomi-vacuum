"""Shared MIoT spec readers and wire exercises for Xiaomi model tests."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Final

from custom_components.dreame_vacuum.dreame.device import DreameVacuumDevice
from custom_components.dreame_vacuum.dreame.exceptions import (
    DeviceException,
    InvalidActionException,
    UnavailableException,
)
from custom_components.dreame_vacuum.dreame.types import (
    DreameVacuumAction,
    DreameVacuumProperty,
    DreameVacuumState,
)
from custom_components.dreame_vacuum.xiaomi import (
    XiaomiControlException,
    invoke_control,
    read_control,
    resolve_family,
    write_control,
)
from custom_components.dreame_vacuum.xiaomi.controls import XiaomiControl
from custom_components.dreame_vacuum.xiaomi.mapping import (
    MODEL_ROBOT_VACUUM_5,
    MODEL_X20_MAX,
    XiaomiModel,
)
from custom_components.dreame_vacuum.xiaomi.model import StoredState
import pytest
from tests.xiaomi.helpers import (
    FakeMiio,
    release_device,
    traffic_outside_map,
    wire_for_state,
)

LOOPBACK_HOST: Final = "127.0.0.1"
LOOPBACK_TOKEN: Final = "00" * 16
LOOPBACK_MAC: Final = "00:00:00:00:00:00"
_SPECS: Final = Path(__file__).parent / "specs"
_STRINGS: Final = Path("custom_components/dreame_vacuum/strings.json")
_WRITE_SAMPLE_LIMIT: Final = 100
_CONTROL_SAMPLE_LIMIT: Final = 255
_EVENT_REASON: Final = (
    "needs council: completion events need a notification design; "
    "the integration polls and does not subscribe to MIoT events."
)
_SERVICE_REASONS: Final[dict[int, str]] = {
    1: "identity: manufacturer, model, and firmware come from miIO.info.",
    10: "map: map, room, and zone support stays off until its own change.",
}
_START_CUSTOM_REASON: Final = (
    "map: room and zone payloads stay unmapped until a Xiaomi codec exists."
)
_START_CUSTOM_ACTIONS: Final = frozenset({(2, 9), (6, 7)})
_REASON_PREFIXES: Final = ("identity:", "map:", "no ha meaning:", "needs council:")
_REFUSED_ACTIONS: Final = (
    DreameVacuumAction.PLAY_SOUND,
    DreameVacuumAction.REQUEST_MAP,
    DreameVacuumAction.BACKUP_MAP,
    DreameVacuumAction.UPDATE_MAP_DATA,
    DreameVacuumAction.RESET_SILVER_ION,
    DreameVacuumAction.START_WASHING,
)


@dataclass(frozen=True, slots=True)
class SpecCase:
    """Model id, spec file, and omission tables for one Xiaomi spec suite."""

    model: str
    device_name: str
    spec_filename: str
    property_reasons: Mapping[tuple[int, int], str]
    action_reasons: Mapping[tuple[int, int], str]
    state_after_read: Mapping[int, DreameVacuumState]
    classification_counts: Mapping[str, tuple[int, int]]
    spec_type: str | None = None
    reason_prefix_counts: Mapping[str, int] | None = None
    absent_items: tuple[tuple[str, int, int], ...] = ()
    checked_events: tuple[tuple[int, int], ...] = ()
    service_reasons: Mapping[int, str] | None = None
    version_only_controls: frozenset[tuple[int, int]] = frozenset()
    version_only_items: frozenset[tuple[str, int, int]] = frozenset()
    action_spec_filenames: tuple[str, ...] = ()
    previous_spec_filename: str | None = None
    state_wire_eight: int | None = 19
    station_shell: bool = True
    required_service_ids: tuple[int, ...] | None = None


# S60+ and S60 omit the same items. Each model maps only its own extra addresses.
S60_CLASS_PROPERTY_REASONS: Final[dict[tuple[int, int], str]] = {
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
    (2, 57): "map: furniture.",
    (2, 58): "map: carpet objects.",
    (2, 65): "map: vacuum route is not readable and is map geometry.",
    (2, 67): "no ha meaning: action result is a command echo.",
    (2, 70): "needs council: plugin reminder text needs a text entity.",
    (2, 99): "map: sill geometry.",
    (2, 102): "map: automation furniture.",
    (2, 103): "map: hidden zones stay unmapped until map support.",
    (2, 106): "no ha meaning: sweep params are neither readable nor writable.",
    (11, 2): "needs council: DND time is one packed integer, not a start and end.",
    (15, 1): "needs council: target voice id encoding is not a Dreame voice property.",
    (15, 5): "no ha meaning: voice url is neither readable nor writable.",
    (15, 6): "no ha meaning: voice common params are neither readable nor writable.",
    (20, 1): "no ha meaning: unnamed field is neither readable nor writable.",
    (20, 2): "no ha meaning: unnamed field is neither readable nor writable.",
    (20, 3): "needs council: unnamed readable string.",
    (20, 6): "needs council: unnamed writable field has no published meaning.",
    (22, 1): "no ha meaning: self-check items are neither readable nor writable.",
}
S60_CLASS_ACTION_REASONS: Final[dict[tuple[int, int], str]] = {
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
    (2, 56): "map: furniture cleaning takes a map parameter.",
    (2, 60): "needs council: operating an AI object takes an opaque parameter.",
    (2, 62): "needs council: common-object clean takes an object parameter.",
    (2, 65): "map: rotating the map takes a parameter and is map geometry.",
    (15, 1): "needs council: voice download takes a pack url.",
    (15, 2): "no ha meaning: download status is already the mapped property.",
    (20, 1): "map: history objects stay unmapped until map support.",
    (20, 2): "needs council: user-defined info takes an opaque parameter.",
    (20, 3): "map: stopping a map upload stays unmapped until map support.",
    (20, 5): "needs council: reading a schedule takes an opaque parameter.",
    (20, 6): "needs council: switching a schedule takes an opaque parameter.",
    (20, 10): "needs council: reading a language pack takes an opaque parameter.",
    (20, 16): "needs council: OTA info takes a parameter and must not start an update.",
}
S60_CLASS_STATE_AFTER_READ: Final[dict[int, DreameVacuumState]] = {
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
    25: DreameVacuumState.UNKNOWN,
    26: DreameVacuumState.CLEAN_SUMMON,
    27: DreameVacuumState.SWEEPING,
}


ROBOT_VACUUM_6_PROPERTY_REASONS: Final[dict[tuple[int, int], str]] = {
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
    (2, 103): "map: hidden zones stay unmapped until map support.",
    (2, 104): "needs council: the command enum is a sweep parameter, not a setting.",
    (2, 105): "needs council: the flag enum is a sweep parameter, not a setting.",
    (2, 106): "no ha meaning: sweep params are neither readable nor writable.",
    (11, 2): "needs council: DND time is one packed integer, not a start and end.",
    (15, 1): "needs council: target voice id encoding is not a Dreame voice property.",
    (15, 5): "no ha meaning: voice url is neither readable nor writable.",
    (15, 6): "no ha meaning: voice common params are neither readable nor writable.",
    (20, 1): "no ha meaning: unnamed field is neither readable nor writable.",
    (20, 2): "no ha meaning: unnamed field is neither readable nor writable.",
    (20, 3): "needs council: unnamed readable string.",
    (20, 4): "no ha meaning: self-check items are neither readable nor writable.",
    (20, 5): "needs council: unnamed readable string.",
    (20, 6): "no ha meaning: spec-test is a vendor test marker, not a user setting.",
    (22, 1): "no ha meaning: self-check items are neither readable nor writable.",
    (23, 1): "map: standard-map room info.",
    (23, 2): "map: standard-map object info.",
    (23, 3): "map: standard-map carpet info.",
}

ROBOT_VACUUM_6_ACTION_REASONS: Final[dict[tuple[int, int], str]] = {
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
    (2, 65): "map: rotating the map takes a parameter and is map geometry.",
    (2, 66): "needs council: sweep takes a sweep-params parameter.",
    (15, 1): "needs council: voice download takes a pack url.",
    (15, 2): "no ha meaning: download status is already the mapped property.",
    (20, 1): "map: history objects stay unmapped until map support.",
    (20, 2): "needs council: user-defined info takes an opaque parameter.",
    (20, 3): "map: stopping a map upload stays unmapped until map support.",
    (
        20,
        4,
    ): "no ha meaning: the Xiaoai bind id is a diagnostic fetch, not a user control.",
    (20, 5): "needs council: reading a schedule takes an opaque parameter.",
    (20, 6): "needs council: switching a schedule takes an opaque parameter.",
    (20, 10): "needs council: reading a language pack takes an opaque parameter.",
    (20, 16): "needs council: reading OTA info takes an opaque parameter.",
}

ROBOT_VACUUM_5_PROPERTY_REASONS: Final[dict[tuple[int, int], str]] = {
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
    (17, 1): "no ha meaning: picture id is neither readable nor writable.",
    (17, 2): "needs council: unnamed picture string has no spec description.",
    (20, 1): "no ha meaning: unnamed field is neither readable nor writable.",
    (20, 2): "no ha meaning: unnamed field is neither readable nor writable.",
    (20, 3): "needs council: unnamed readable string.",
    (20, 4): "needs council: self-check values are internal component codes.",
    (20, 5): "needs council: unnamed readable string.",
    (20, 6): "needs council: unnamed writable field has no spec description.",
    (20, 12): "no ha meaning: unnamed field is neither readable nor writable.",
}

ROBOT_VACUUM_5_ACTION_REASONS: Final[dict[tuple[int, int], str]] = {
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
    (2, 42): "needs council: starting a user sweep takes an id parameter.",
    (2, 47): "map: the vacuum route takes a parameter and is map geometry.",
    (2, 48): "needs council: closing an abnormal card takes an opaque parameter.",
    (2, 52): "map: skip cleaning takes a room-id parameter.",
    (2, 53): "map: final cleaning takes a room-id parameter.",
    (2, 54): "map: temporary room cleaning takes a room-id parameter.",
    (2, 55): "map: temporary zone cleaning takes a zone parameter.",
    (2, 56): "map: furniture cleaning takes a map parameter.",
    (2, 60): "needs council: AI recognize takes an object parameter.",
    (2, 62): "needs council: common-object clean takes an object parameter.",
    (15, 1): "needs council: voice download takes a pack url.",
    (15, 2): "no ha meaning: download status is already the mapped property.",
    (17, 1): "needs council: the picture request takes an id and returns an image.",
    (20, 1): "map: history objects stay unmapped until map support.",
    (20, 2): "needs council: user-defined info takes an opaque parameter.",
    (20, 3): "map: stopping a map upload stays unmapped until map support.",
    (
        20,
        7,
    ): "needs council: lidar control takes a parameter and must not enable map support.",
}


ROBOT_VACUUM_5_PRO_PROPERTY_REASONS: Final[dict[tuple[int, int], str]] = {
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
    (2, 103): "map: hidden zone geometry.",
    (11, 2): "needs council: DND time is one packed integer, not a start and end.",
    (15, 1): "needs council: target voice id encoding is not a Dreame voice property.",
    (15, 5): "no ha meaning: voice url is neither readable nor writable.",
    (15, 6): "no ha meaning: voice common params are neither readable nor writable.",
    (20, 1): "no ha meaning: unnamed field is neither readable nor writable.",
    (20, 2): "no ha meaning: unnamed field is neither readable nor writable.",
    (20, 3): "needs council: unnamed readable string.",
    (17, 1): "no ha meaning: unnamed field is neither readable nor writable.",
    (17, 2): "needs council: unnamed readable string.",
    (20, 4): "no ha meaning: self-check items are neither readable nor writable.",
    (20, 5): "needs council: self-check result has no published description.",
    (20, 6): "needs council: unnamed writable field has no published meaning.",
    (20, 12): "no ha meaning: lidar button type is neither readable nor writable.",
    (21, 1): "map: cruise position is map geometry.",
    (21, 7): "no ha meaning: stream common params are neither readable nor writable.",
}

ROBOT_VACUUM_5_PRO_ACTION_REASONS: Final[dict[tuple[int, int], str]] = {
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
    (2, 65): "map: rotating the map takes a parameter and is map geometry.",
    (15, 1): "needs council: voice download takes a pack url.",
    (15, 2): "no ha meaning: download status is already the mapped property.",
    (20, 1): "map: history objects stay unmapped until map support.",
    (20, 2): "needs council: user-defined info takes an opaque parameter.",
    (20, 3): "map: stopping a map upload stays unmapped until map support.",
    (20, 5): "needs council: reading a schedule takes an opaque parameter.",
    (20, 6): "needs council: switching a schedule takes an opaque parameter.",
    (
        20,
        7,
    ): "needs council: lidar control takes a parameter and must not enable map support.",
    (20, 8): "needs council: starting a patrol takes an opaque parameter.",
    (17, 1): "map: AI pictures stay unmapped until map support.",
    (21, 1): "needs council: auto cruise takes an opaque parameter.",
    (21, 2): "needs council: arriving at a place takes an opaque parameter.",
    (21, 4): "needs council: entering the video page takes an opaque parameter.",
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


H50_PRO_PROPERTY_REASONS: Final[dict[tuple[int, int], str]] = {
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
    (20, 6): "needs council: unnamed writable field has no published meaning.",
    (20, 13): "needs council: unnamed writable field has no published meaning.",
    (22, 1): "no ha meaning: self-check items are neither readable nor writable.",
}

H50_PRO_ACTION_REASONS: Final[dict[tuple[int, int], str]] = {
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
    (2, 62): "needs council: common-object clean takes an object parameter.",
    (15, 1): "needs council: voice download takes a pack url.",
    (15, 2): "no ha meaning: download status is already the mapped property.",
    (20, 1): "map: history objects stay unmapped until map support.",
    (20, 2): "needs council: user-defined info takes an opaque parameter.",
    (20, 3): "map: stopping a map upload stays unmapped until map support.",
    (20, 5): "needs council: reading a schedule takes an opaque parameter.",
    (20, 6): "needs council: switching a schedule takes an opaque parameter.",
    (2, 60): "needs council: operating an AI object takes an opaque parameter.",
    (2, 61): "map: AI picture objects stay unmapped until map support.",
    (17, 1): "map: AI pictures stay unmapped until map support.",
}


_SCHEDULE_REASON: Final = "needs council: schedule editing takes an order blob."
_SWEEP_SCHEDULE_PROPERTIES: Final = tuple(range(1, 20))
SWEEP_PROPERTY_REASONS: Final[dict[tuple[int, int], str]] = {
    (7, 16): "needs council: remote direction is a momentary command, not a setting.",
    (
        7,
        17,
    ): "no ha meaning: consumable index is an action parameter and is not readable.",
    (7, 20): "needs council: timezone offset is not the Dreame timezone property.",
    (7, 21): "needs council: current language is an opaque string.",
    (7, 24): "map: room ids stay unmapped until map support.",
    (7, 25): "map: room clean mode stays unmapped until map support.",
    (7, 26): "map: room clean operation stays unmapped until map support.",
    (7, 27): "no ha meaning: clean-record start time is neither readable nor writable.",
    (7, 28): "no ha meaning: clean-record duration is neither readable nor writable.",
    (7, 29): "no ha meaning: clean-record area is neither readable nor writable.",
    (7, 30): "map: clean-record map url is map data.",
    (7, 31): "no ha meaning: clean-record mode is neither readable nor writable.",
    (7, 32): "no ha meaning: clean-record way is neither readable nor writable.",
    (
        7,
        33,
    ): "no ha meaning: current map id parameter is neither readable nor writable.",
    (7, 34): "no ha meaning: clean preference is neither readable nor writable.",
    (
        7,
        37,
    ): "no ha meaning: clean-record task status is neither readable nor writable.",
    (7, 43): "no ha meaning: go-charging parameter is neither readable nor writable.",
    (7, 45): "needs council: multi-property vacuum blob has no published fields.",
    (7, 48): "needs council: consumables info is an opaque string.",
    (7, 49): "map: charge pose is dock geometry.",
    **{(8, iid): _SCHEDULE_REASON for iid in _SWEEP_SCHEDULE_PROPERTIES},
    (9, 2): "map: zone points are map geometry.",
    (9, 3): "map: restricted points are map geometry.",
    (9, 4): "map: pause type is a zone-clean parameter.",
    (9, 5): "map: target point is map geometry.",
    (9, 6): "map: beauty point is map geometry.",
    (9, 7): "map: map id is map geometry.",
    (9, 8): "map: map type is map geometry.",
    (9, 9): "map: zone timestamp is map geometry.",
    (12, 6): "no ha meaning: DND timezone is neither readable nor writable.",
    (12, 7): "needs council: DND period is one packed string, not a start and end.",
    (14, 1): "no ha meaning: target voice is neither readable nor writable.",
    (14, 2): "no ha meaning: current voice is neither readable nor writable.",
    (14, 3): "no ha meaning: voice download status is neither readable nor writable.",
    (14, 4): "no ha meaning: voice download progress is neither readable nor writable.",
    (14, 5): "no ha meaning: voice url is neither readable nor writable.",
    (14, 6): "no ha meaning: voice checksum is neither readable nor writable.",
}
SWEEP_ACTION_REASONS: Final[dict[tuple[int, int], str]] = {
    (7, 3): "map: room clean takes room ids.",
    (7, 7): "needs council: go-charging takes a start or stop parameter.",
    (8, 1): "needs council: adding a schedule takes an order blob.",
    (8, 2): "needs council: deleting a schedule takes an order id.",
    (8, 3): "needs council: reading schedules returns an order blob.",
    (8, 4): "needs council: adding a schedule takes an order blob.",
    (8, 5): "needs council: schedule count takes a map id.",
    (9, 1): "map: point clean stays unmapped until map support.",
    (9, 2): "map: pausing point clean takes a pause-type parameter.",
    (9, 3): "map: zone clean stays unmapped until map support.",
    (9, 4): "map: pausing zone clean takes a pause-type parameter.",
    (9, 5): "map: beauty wall takes a geometry parameter.",
    (9, 6): "map: virtual wall takes a geometry parameter.",
    (9, 8): "map: zone points take a geometry parameter.",
    (12, 1): "needs council: DND schedule takes six parameters.",
    (14, 1): "needs council: voice download takes a pack url.",
    (14, 2): "needs council: voice download status is not a Dreame voice property.",
    (14, 3): "no ha meaning: update log is a vendor upload, not a user control.",
    (14, 4): "no ha meaning: clearing a voice download is not a user setting.",
}
SWEEP_STATE_AFTER_READ: Final[dict[int, DreameVacuumState]] = {
    0: DreameVacuumState.IDLE,
    1: DreameVacuumState.IDLE,
    2: DreameVacuumState.PAUSED,
    3: DreameVacuumState.RETURNING,
    4: DreameVacuumState.CHARGING,
    5: DreameVacuumState.SWEEPING,
    6: DreameVacuumState.SWEEPING_AND_MOPPING,
    7: DreameVacuumState.MOPPING,
    8: DreameVacuumState.UPGRADING,
}


_X20_DROPPED_SWEEP_PROPERTIES: Final = {(7, 48), (7, 49)}
_X20_ABSENT_SWEEP_ACTIONS: Final = {(14, 3), (14, 4)}
X20_PROPERTY_REASONS: Final[dict[tuple[int, int], str]] = {
    key: reason
    for key, reason in SWEEP_PROPERTY_REASONS.items()
    if key not in _X20_DROPPED_SWEEP_PROPERTIES
}
X20_PROPERTY_REASONS.update(
    {
        (2, 9): "needs council: switch status is a string, not a boolean.",
        (2, 10): "map: room ids stay unmapped until map support.",
        (7, 38): "no ha meaning: clean preference type is an action parameter.",
        (7, 39): "no ha meaning: clean preference switch is an action parameter.",
        (7, 40): "no ha meaning: clean preference is neither readable nor writable.",
        (
            7,
            41,
        ): "no ha meaning: clean preference switch is an action parameter.",
        (7, 46): "no ha meaning: the sd flag is neither readable nor writable.",
        (7, 52): "map: carpet display is map rendering.",
        (
            7,
            53,
        ): "no ha meaning: station act is an action parameter and is not readable.",
        (7, 55): "map: map encryption stays unmapped until map support.",
        (7, 61): "no ha meaning: left time is neither readable nor writable.",
        (
            15,
            1,
        ): "needs council: standard filter life repeats the named sweep filter.",
        (
            15,
            2,
        ): "needs council: standard filter time repeats the named sweep filter.",
        (
            16,
            1,
        ): "needs council: the two brush services are identical, so neither is mapped.",
        (
            16,
            2,
        ): "needs council: the two brush services are identical, so neither is mapped.",
        (
            17,
            1,
        ): "needs council: the two brush services are identical, so neither is mapped.",
        (
            17,
            2,
        ): "needs council: the two brush services are identical, so neither is mapped.",
        (18, 1): "needs council: standard mop life repeats the named sweep mop.",
        (18, 2): "needs council: standard mop time repeats the named sweep mop.",
    }
)
X20_ACTION_REASONS: Final[dict[tuple[int, int], str]] = {
    key: reason
    for key, reason in SWEEP_ACTION_REASONS.items()
    if key not in _X20_ABSENT_SWEEP_ACTIONS
}
X20_ACTION_REASONS.update(
    {
        (2, 7): "map: room sweep takes a room-id parameter.",
        (7, 4): "needs council: setting a clean preference takes an opaque parameter.",
        (7, 5): "needs council: reading a clean preference takes an opaque parameter.",
        (7, 6): "needs council: setting a preference type takes an opaque parameter.",
        (7, 8): "needs council: erasing a preference takes an opaque parameter.",
        (7, 9): "needs council: setting a clean preference takes an opaque parameter.",
        (7, 10): "needs council: reading a clean preference takes an opaque parameter.",
        (7, 11): "needs council: station action takes a station-act parameter.",
        (7, 12): "needs council: mop-clean-left-time has no published effect.",
        (9, 9): "map: point clean stays unmapped until map support.",
        (
            15,
            1,
        ): "needs council: filter reset stays on the sweep consumable action.",
        (
            16,
            1,
        ): "needs council: the two brush resets cannot be told apart.",
        (
            17,
            1,
        ): "needs council: the two brush resets cannot be told apart.",
        (18, 1): "needs council: mop reset stays on the sweep consumable action.",
    }
)
X20_STATE_AFTER_READ: Final[dict[int, DreameVacuumState]] = {
    **SWEEP_STATE_AFTER_READ,
    9: DreameVacuumState.WASHING,
    10: DreameVacuumState.DRYING,
    11: DreameVacuumState.AUTO_EMPTYING,
    12: DreameVacuumState.PAUSED,
}

_S20_DROPPED_SWEEP_PROPERTIES: Final = {(7, 48), (7, 49)}
_S20_ABSENT_SWEEP_ACTIONS: Final = {(14, 3), (14, 4)}
S20_PROPERTY_REASONS: Final[dict[tuple[int, int], str]] = {
    key: reason
    for key, reason in SWEEP_PROPERTY_REASONS.items()
    if key not in _S20_DROPPED_SWEEP_PROPERTIES
}
S20_PROPERTY_REASONS.update(
    {
        (2, 9): "needs council: switch status is a string, not a boolean.",
        (2, 10): "map: room ids stay unmapped until map support.",
        (7, 38): "no ha meaning: clean preference type is an action parameter.",
        (7, 39): "no ha meaning: clean preference switch is an action parameter.",
        (7, 40): "no ha meaning: clean preference is neither readable nor writable.",
        (
            7,
            41,
        ): "no ha meaning: clean preference switch is an action parameter.",
        (7, 46): "no ha meaning: the sd flag is neither readable nor writable.",
        (7, 52): "map: carpet display is map rendering.",
        (7, 55): "map: map encryption stays unmapped until map support.",
        (
            15,
            1,
        ): "needs council: standard filter life repeats the named sweep filter.",
        (
            15,
            2,
        ): "needs council: standard filter time repeats the named sweep filter.",
        (
            16,
            1,
        ): "needs council: the two brush services are identical, so neither is mapped.",
        (
            16,
            2,
        ): "needs council: the two brush services are identical, so neither is mapped.",
        (
            17,
            1,
        ): "needs council: the two brush services are identical, so neither is mapped.",
        (
            17,
            2,
        ): "needs council: the two brush services are identical, so neither is mapped.",
        (18, 1): "needs council: standard mop life repeats the named sweep mop.",
        (18, 2): "needs council: standard mop time repeats the named sweep mop.",
    }
)
S20_ACTION_REASONS: Final[dict[tuple[int, int], str]] = {
    key: reason
    for key, reason in SWEEP_ACTION_REASONS.items()
    if key not in _S20_ABSENT_SWEEP_ACTIONS
}
S20_ACTION_REASONS.update(
    {
        (2, 7): "map: room sweep takes a room-id parameter.",
        (2, 11): "map: room sweep takes a room-id parameter.",
        (7, 4): "needs council: setting a clean preference takes an opaque parameter.",
        (7, 5): "needs council: reading a clean preference takes an opaque parameter.",
        (7, 6): "needs council: setting a preference type takes an opaque parameter.",
        (7, 8): "needs council: erasing a preference takes an opaque parameter.",
        (7, 9): "needs council: setting a clean preference takes an opaque parameter.",
        (7, 10): "needs council: reading a clean preference takes an opaque parameter.",
        (7, 11): "needs council: listening voice has no published effect.",
        (9, 9): "map: point clean stays unmapped until map support.",
        (
            15,
            1,
        ): "needs council: filter reset stays on the sweep consumable action.",
        (
            16,
            1,
        ): "needs council: the two brush resets cannot be told apart.",
        (
            17,
            1,
        ): "needs council: the two brush resets cannot be told apart.",
        (18, 1): "needs council: mop reset stays on the sweep consumable action.",
    }
)
S20_STATE_AFTER_READ: Final[dict[int, DreameVacuumState]] = {
    **SWEEP_STATE_AFTER_READ,
    9: DreameVacuumState.BUILDING,
    10: DreameVacuumState.CHARGING,
}

X20_PRO_PROPERTY_REASONS: Final[dict[tuple[int, int], str]] = {
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
    (2, 57): "map: furniture.",
    (2, 58): "map: carpet objects.",
    (2, 65): "map: vacuum route is not readable and is map geometry.",
    (2, 67): "no ha meaning: action result is a command echo.",
    (2, 70): "needs council: plugin reminder text needs a text entity.",
    (11, 2): "needs council: DND time is one packed integer, not a start and end.",
    (15, 1): "needs council: target voice id encoding is not a Dreame voice property.",
    (15, 5): "no ha meaning: voice url is neither readable nor writable.",
    (15, 6): "no ha meaning: voice common params are neither readable nor writable.",
    (20, 1): "no ha meaning: unnamed field is neither readable nor writable.",
    (20, 2): "no ha meaning: unnamed field is neither readable nor writable.",
    (20, 3): "needs council: unnamed readable string.",
}

X20_PRO_ACTION_REASONS: Final[dict[tuple[int, int], str]] = {
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
    (2, 42): "needs council: starting a user sweep takes an id parameter.",
    (2, 47): "map: the vacuum route takes a parameter and is map geometry.",
    (2, 48): "needs council: closing an abnormal card takes an opaque parameter.",
    (15, 1): "needs council: voice download takes a pack url.",
    (15, 2): "no ha meaning: download status is already the mapped property.",
    (20, 1): "map: history objects stay unmapped until map support.",
    (20, 2): "needs council: user-defined info takes an opaque parameter.",
    (20, 3): "map: stopping a map upload stays unmapped until map support.",
}

X20_PRO_STATE_AFTER_READ: Final[dict[int, DreameVacuumState]] = {
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
}

VACUUM_6_MAX_PROPERTY_REASONS: Final[dict[tuple[int, int], str]] = {
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
    (2, 103): "map: hidden zones stay unmapped until map support.",
    (11, 2): "needs council: DND time is one packed integer, not a start and end.",
    (15, 1): "needs council: target voice id encoding is not a Dreame voice property.",
    (15, 5): "no ha meaning: voice url is neither readable nor writable.",
    (15, 6): "no ha meaning: voice common params are neither readable nor writable.",
    (20, 1): "no ha meaning: unnamed field is neither readable nor writable.",
    (20, 2): "no ha meaning: unnamed field is neither readable nor writable.",
    (20, 3): "needs council: unnamed readable string.",
    (20, 4): "no ha meaning: self-check items are neither readable nor writable.",
    (20, 5): "needs council: unnamed readable string.",
    (20, 6): "needs council: unnamed writable field has no published meaning.",
    (20, 12): "no ha meaning: unnamed field is neither readable nor writable.",
    (20, 14): "needs council: unnamed readable string.",
    (20, 15): "needs council: unnamed readable string.",
    (21, 7): "no ha meaning: stream common params are neither readable nor writable.",
    (22, 1): "no ha meaning: self-check items are neither readable nor writable.",
}

VACUUM_6_MAX_ACTION_REASONS: Final[dict[tuple[int, int], str]] = {
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
    (2, 65): "map: rotating the map takes a parameter and is map geometry.",
    (15, 1): "needs council: voice download takes a pack url.",
    (15, 2): "no ha meaning: download status is already the mapped property.",
    (20, 1): "map: history objects stay unmapped until map support.",
    (20, 2): "needs council: user-defined info takes an opaque parameter.",
    (20, 3): "map: stopping a map upload stays unmapped until map support.",
    (
        20,
        4,
    ): "no ha meaning: the Xiaoai bind id is a diagnostic fetch, not a user control.",
    (20, 5): "needs council: reading a schedule takes an opaque parameter.",
    (20, 6): "needs council: switching a schedule takes an opaque parameter.",
    (
        20,
        7,
    ): "needs council: lidar control takes a parameter and must not enable map support.",
    (20, 8): "needs council: starting a patrol takes an opaque parameter.",
    (20, 10): "needs council: reading a language pack takes an opaque parameter.",
    (20, 12): "needs council: acknowledging a check result takes an opaque parameter.",
    (20, 13): "needs council: reading the check result takes an opaque parameter.",
    (20, 14): "needs council: leaving check mode takes an opaque parameter.",
    (20, 15): "needs council: starting a check task takes an opaque parameter.",
    (21, 4): "needs council: entering the video page takes an opaque parameter.",
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

VACUUM_6_MAX_STATE_AFTER_READ: Final[dict[int, DreameVacuumState]] = {
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
    24: DreameVacuumState.RETURNING,
    25: DreameVacuumState.UNKNOWN,
    26: DreameVacuumState.CLEAN_SUMMON,
    27: DreameVacuumState.SWEEPING,
}

VACUUM_6_PRO_PROPERTY_REASONS: Final[dict[tuple[int, int], str]] = {
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
    (2, 103): "map: hidden zones stay unmapped until map support.",
    (11, 2): "needs council: DND time is one packed integer, not a start and end.",
    (15, 1): "needs council: target voice id encoding is not a Dreame voice property.",
    (15, 5): "no ha meaning: voice url is neither readable nor writable.",
    (15, 6): "no ha meaning: voice common params are neither readable nor writable.",
    (20, 1): "no ha meaning: unnamed field is neither readable nor writable.",
    (20, 2): "no ha meaning: unnamed field is neither readable nor writable.",
    (20, 3): "needs council: unnamed readable string.",
    (20, 4): "no ha meaning: self-check items are neither readable nor writable.",
    (20, 5): "needs council: unnamed readable string.",
    (20, 6): "needs council: unnamed writable field has no published meaning.",
    (20, 12): "no ha meaning: unnamed field is neither readable nor writable.",
    (20, 14): "needs council: unnamed readable string.",
    (20, 15): "needs council: unnamed readable string.",
    (21, 7): "no ha meaning: stream common params are neither readable nor writable.",
    (22, 1): "no ha meaning: self-check items are neither readable nor writable.",
}

VACUUM_6_PRO_ACTION_REASONS: Final[dict[tuple[int, int], str]] = {
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
    (2, 65): "map: rotating the map takes a parameter and is map geometry.",
    (15, 1): "needs council: voice download takes a pack url.",
    (15, 2): "no ha meaning: download status is already the mapped property.",
    (20, 1): "map: history objects stay unmapped until map support.",
    (20, 2): "needs council: user-defined info takes an opaque parameter.",
    (20, 3): "map: stopping a map upload stays unmapped until map support.",
    (
        20,
        4,
    ): "no ha meaning: the Xiaoai bind id is a diagnostic fetch, not a user control.",
    (20, 5): "needs council: reading a schedule takes an opaque parameter.",
    (20, 6): "needs council: switching a schedule takes an opaque parameter.",
    (
        20,
        7,
    ): "needs council: lidar control takes a parameter and must not enable map support.",
    (20, 8): "needs council: starting a patrol takes an opaque parameter.",
    (20, 10): "needs council: reading a language pack takes an opaque parameter.",
    (20, 12): "needs council: acknowledging a check result takes an opaque parameter.",
    (20, 13): "needs council: reading the check result takes an opaque parameter.",
    (20, 14): "needs council: leaving check mode takes an opaque parameter.",
    (20, 15): "needs council: starting a check task takes an opaque parameter.",
    (21, 4): "needs council: entering the video page takes an opaque parameter.",
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

VACUUM_6_PRO_STATE_AFTER_READ: Final[dict[int, DreameVacuumState]] = {
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
    25: DreameVacuumState.UNKNOWN,
    26: DreameVacuumState.CLEAN_SUMMON,
}


MIJIA_B108_SERVICE_REASONS: Final[dict[int, str]] = {
    1: "identity: manufacturer, model, and firmware come from miIO.info.",
    7: "map: map, room, and zone support stays off until its own change.",
}
MIJIA_B108_PROPERTY_REASONS: Final[dict[tuple[int, int], str]] = {
    (2, 10): "map: zone ids.",
    (2, 11): "map: restricted areas.",
    (2, 12): "map: virtual walls.",
    (2, 13): "map: room ids are not readable.",
    (2, 14): "map: room name is not readable.",
    (2, 15): "map: points are not readable.",
    (3, 3): "no ha meaning: battery voltage is not a Home Assistant battery sensor.",
    (5, 2): "no ha meaning: current lock echoes the mapped child lock.",
    (6, 2): "no ha meaning: firmware is already exposed from miIO.info.",
    (6, 4): "needs council: DND time is one packed integer, not a start and end.",
    (6, 8): "map: carpet display is map rendering.",
    (6, 10): "map: room information.",
    (6, 12): "no ha meaning: common params are neither readable nor writable.",
}
MIJIA_B108_ACTION_REASONS: Final[dict[tuple[int, int], str]] = {
    (2, 3): "needs council: sweep-only start duplicates cleaning mode plus start.",
    (2, 4): "needs council: mop start duplicates cleaning mode plus start.",
    (2, 5): "needs council: sweep-mop start duplicates cleaning mode plus start.",
    (2, 7): "map: zone config takes a room-id parameter.",
    (2, 8): "map: room config takes a room-id parameter.",
    (2, 9): "map: set-zone takes a zone parameter.",
    (2, 10): "map: room clean config takes a room parameter.",
    (2, 11): "map: split room is a map edit.",
    (2, 12): "map: merge rooms is a map edit.",
    (2, 13): "map: room sweep takes a room-id parameter.",
    (2, 14): "map: build-map stays unmapped until map support.",
    (6, 2): "needs council: entering remote control needs a remote-control design.",
    (6, 3): "needs council: adding a schedule takes an order blob.",
    (6, 4): "needs council: modifying a schedule takes an order blob.",
    (6, 5): "needs council: deleting a schedule takes an order blob.",
    (6, 8): "needs council: listening voice has no published effect.",
    (6, 9): "needs council: remote direction buttons need a remote-control design.",
    (6, 10): "needs council: remote direction buttons need a remote-control design.",
    (6, 11): "needs council: remote direction buttons need a remote-control design.",
    (6, 12): "needs council: remote direction buttons need a remote-control design.",
    (6, 13): "needs council: remote direction buttons need a remote-control design.",
    (6, 14): "needs council: remote direction buttons need a remote-control design.",
    (6, 15): "needs council: stop-and-gocharge duplicates return-to-base.",
    (6, 16): "no ha meaning: system info is a diagnostic fetch, not a user control.",
}
MIJIA_B108_STATE_AFTER_READ: Final[dict[int, DreameVacuumState]] = {
    1: DreameVacuumState.IDLE,
    2: DreameVacuumState.CHARGING,
    3: DreameVacuumState.CHARGING,
    4: DreameVacuumState.SWEEPING,
    5: DreameVacuumState.PAUSED,
    6: DreameVacuumState.RETURNING,
    7: DreameVacuumState.REMOTE_CONTROL,
    8: DreameVacuumState.CHARGING_COMPLETED,
    9: DreameVacuumState.BUILDING,
    10: DreameVacuumState.UPGRADING,
}


def mijia_b108_case(
    model: str, device_name: str, spec_filename: str, spec_type: str
) -> SpecCase:
    """Build the shared 2S spec case for one released mijia.vacuum.b108 model."""
    return SpecCase(
        model=model,
        device_name=device_name,
        spec_filename=spec_filename,
        property_reasons=MIJIA_B108_PROPERTY_REASONS,
        action_reasons=MIJIA_B108_ACTION_REASONS,
        state_after_read=MIJIA_B108_STATE_AFTER_READ,
        classification_counts={spec_filename: (42, 60)},
        spec_type=spec_type,
        reason_prefix_counts={
            "identity": 5,
            "map": 31,
            "needs council": 19,
            "no ha meaning": 5,
        },
        service_reasons=MIJIA_B108_SERVICE_REASONS,
        checked_events=((3, 1), (7, 1), (7, 2)),
        state_wire_eight=int(DreameVacuumState.CHARGING_COMPLETED),
        action_spec_filenames=(spec_filename,),
    )


def sweep_case(
    model: str, device_name: str, spec_filename: str, spec_type: str
) -> SpecCase:
    """Build the shared E10-family spec case for one released model."""
    return SpecCase(
        model=model,
        device_name=device_name,
        spec_filename=spec_filename,
        property_reasons=SWEEP_PROPERTY_REASONS,
        action_reasons=SWEEP_ACTION_REASONS,
        state_after_read=SWEEP_STATE_AFTER_READ,
        classification_counts={spec_filename: (36, 135)},
        spec_type=spec_type,
        reason_prefix_counts={
            "identity": 5,
            "map": 64,
            "needs council": 47,
            "no ha meaning": 19,
        },
        state_wire_eight=int(DreameVacuumState.UPGRADING),
        station_shell=False,
        action_spec_filenames=(spec_filename,),
    )


def load_spec_document(filename: str) -> dict[str, object]:
    """Load one published MIoT spec document."""
    loaded = json.loads((_SPECS / filename).read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def spec_items(filename: str) -> list[tuple[str, int, int, dict[str, object]]]:
    """Return every property, action, and event as kind, siid, iid, and spec."""
    found: list[tuple[str, int, int, dict[str, object]]] = []
    document = load_spec_document(filename)
    services = document["services"]
    assert isinstance(services, list)
    for service in services:
        assert isinstance(service, dict)
        siid = service["iid"]
        assert isinstance(siid, int)
        for kind, field in (
            ("property", "properties"),
            ("action", "actions"),
            ("event", "events"),
        ):
            raw = service.get(field) or []
            assert isinstance(raw, list)
            for item in raw:
                assert isinstance(item, dict)
                iid = item["iid"]
                assert isinstance(iid, int)
                found.append((kind, siid, iid, item))
    return found


def with_reason_overrides(
    base: Mapping[tuple[int, int], str],
    *,
    drop: tuple[tuple[int, int], ...] = (),
    add: Mapping[tuple[int, int], str] | None = None,
) -> dict[tuple[int, int], str]:
    """Copy an omission table, drop addresses the spec lacks, and add new ones."""
    merged = dict(base)
    for key in drop:
        if key not in merged:
            raise KeyError(key)
        del merged[key]
    if not add:
        return merged
    overlap = set(add) & set(merged)
    if overlap:
        raise KeyError(next(iter(overlap)))
    merged.update(add)
    return merged


# Mijia 7 Max publishes a shorter status list than Robot Vacuum 6 Max.
_MIJIA_7_MAX_ABSENT_STATUS_WIRES: Final = frozenset({15, 16, 17, 24, 27})
MIJIA_7_MAX_PROPERTY_REASONS: Final[dict[tuple[int, int], str]] = with_reason_overrides(
    VACUUM_6_MAX_PROPERTY_REASONS,
    drop=((20, 12),),
    add={
        (2, 104): ROBOT_VACUUM_6_PROPERTY_REASONS[(2, 104)],
        (2, 105): ROBOT_VACUUM_6_PROPERTY_REASONS[(2, 105)],
        (2, 106): ROBOT_VACUUM_6_PROPERTY_REASONS[(2, 106)],
        (17, 1): "no ha meaning: unnamed field is neither readable nor writable.",
        (17, 2): "map: AI picture data stays unmapped until map support.",
        (20, 17): "needs council: unnamed writable string.",
        (20, 18): "needs council: unnamed readable string.",
        (23, 1): ROBOT_VACUUM_6_PROPERTY_REASONS[(23, 1)],
        (23, 2): ROBOT_VACUUM_6_PROPERTY_REASONS[(23, 2)],
        (23, 3): ROBOT_VACUUM_6_PROPERTY_REASONS[(23, 3)],
        (26, 1): "needs council: home environment info is an opaque string.",
    },
)
MIJIA_7_MAX_ACTION_REASONS: Final[dict[tuple[int, int], str]] = with_reason_overrides(
    VACUUM_6_MAX_ACTION_REASONS,
    drop=((20, 7),),
    add={
        (2, 66): ROBOT_VACUUM_6_ACTION_REASONS[(2, 66)],
        (17, 1): (
            "map: requesting an AI picture takes a parameter and stays "
            "unmapped until map support."
        ),
        (20, 11): "needs council: entering check mode takes a parameter.",
        (20, 16): ROBOT_VACUUM_6_ACTION_REASONS[(20, 16)],
    },
)
MIJIA_7_MAX_STATE_AFTER_READ: Final[dict[int, DreameVacuumState]] = {
    wire: state
    for wire, state in VACUUM_6_MAX_STATE_AFTER_READ.items()
    if wire not in _MIJIA_7_MAX_ABSENT_STATUS_WIRES
}


def spec_index(filename: str) -> dict[tuple[str, int, int], dict[str, object]]:
    """Index one spec by kind, siid, and iid."""
    return {(kind, siid, iid): spec for kind, siid, iid, spec in spec_items(filename)}


def normalize_spec(value: object, model_codes: tuple[str, ...]) -> object:
    """Replace model codes in spec text so two documents can be compared."""
    if isinstance(value, str):
        normalized = value
        for code in model_codes:
            normalized = normalized.replace(code, "model")
        return normalized
    if isinstance(value, dict):
        return {key: normalize_spec(item, model_codes) for key, item in value.items()}
    if isinstance(value, list):
        return [normalize_spec(item, model_codes) for item in value]
    return value


def comparable_spec_item(value: object, model_codes: tuple[str, ...]) -> object:
    """Drop identity URNs and empty GATT access so two items can be compared."""
    normalized = normalize_spec(value, model_codes)
    if isinstance(normalized, dict):
        return {
            key: item
            for key, item in normalized.items()
            if key not in {"type", "gatt-access"}
        }
    return normalized


def spec_samples(
    spec: Mapping[str, object],
    *,
    full_range_limit: int | None = None,
) -> list[object]:
    """Return wire samples for one property spec.

    When full_range_limit is set and the inclusive range spans at most that
    many steps, every value is returned. Otherwise the samples are the ends
    and the midpoint.
    """
    if spec.get("format") == "bool":
        return [False, True]
    listed = spec.get("value-list")
    if isinstance(listed, list):
        return [item["value"] for item in listed if isinstance(item, dict)]
    bounds = _range_bounds(spec)
    if bounds is not None:
        start, end, step = bounds
        if full_range_limit is not None and (end - start) // step <= full_range_limit:
            return list(range(start, end + 1, step))
        middle = start + ((end - start) // 2)
        middle -= (middle - start) % step
        return list(dict.fromkeys((start, middle, end)))
    if spec.get("format") == "string":
        return ["", "sample"]
    return [0, 1]


def omission_reason(
    kind: str,
    siid: int,
    iid: int,
    *,
    property_reasons: Mapping[tuple[int, int], str],
    action_reasons: Mapping[tuple[int, int], str],
    service_reasons: Mapping[int, str] | None = None,
) -> str | None:
    """Return the omission reason for one spec item, or None when it is mapped."""
    if kind == "event":
        return _EVENT_REASON
    if kind == "action" and (siid, iid) in _START_CUSTOM_ACTIONS:
        table = action_reasons
        if (siid, iid) not in table:
            return _START_CUSTOM_REASON
    services = _SERVICE_REASONS if service_reasons is None else service_reasons
    if siid in services:
        return services[siid]
    table = property_reasons if kind == "property" else action_reasons
    return table.get((siid, iid))


def mapped_addresses(family: XiaomiModel, kind: str) -> dict[tuple[int, int], str]:
    """Return mapped addresses and the property, action, or control that owns each."""
    found: dict[tuple[int, int], str] = {}
    if kind == "property":
        for name, item in family.property_overrides.items():
            found[(item["siid"], item["piid"])] = name
        for control in family.controls:
            if control.piid is None or control.siid is None:
                continue
            pair = (control.siid, control.piid)
            assert pair not in found
            found[pair] = control.key
        return found
    for name, item in family.action_overrides.items():
        found[(item["siid"], item["aiid"])] = name
    for control in family.controls:
        if control.aiid is None or control.siid is None:
            continue
        pair = (control.siid, control.aiid)
        if pair in found:
            assert control.action_parameters
            continue
        found[pair] = control.key
    return found


def property_address(family: XiaomiModel, name: str) -> tuple[int, int]:
    """Return the siid and piid of one mapped property."""
    mapping = family.property_overrides[name]
    return mapping["siid"], mapping["piid"]


def spec_description(filename: str, kind: str, siid: int, iid: int) -> str:
    """Return the description of one spec item."""
    for item_kind, item_siid, item_iid, spec in spec_items(filename):
        if item_kind == kind and item_siid == siid and item_iid == iid:
            description = spec.get("description") or ""
            assert isinstance(description, str)
            return description
    raise AssertionError((filename, kind, siid, iid))


def assert_control_options(control: XiaomiControl, spec: Mapping[str, object]) -> None:
    """Assert a control's option values follow the spec value list, in order."""
    listed = spec.get("value-list")
    assert isinstance(listed, list)
    values = [item["value"] for item in listed if isinstance(item, dict)]
    assert [value for value, _slug in control.options] == values


def assert_control_matches_spec(
    control: XiaomiControl, spec: Mapping[str, object]
) -> None:
    """Assert one control's access, options, and range follow its spec item."""
    if control.aiid is not None:
        assert list(spec.get("in") or []) == [
            piid for piid, _value in control.action_parameters
        ], control.key
        return
    access = spec.get("access")
    assert isinstance(access, list)
    assert control.writable is ("write" in access)
    if control.options:
        assert_control_options(control, spec)
        return
    if control.value_kind == "bool":
        assert spec.get("format") == "bool"
        return
    if control.value_kind == "string":
        assert spec.get("format") == "string"
        return
    bounds = spec.get("value-range")
    assert bounds == [control.minimum, control.maximum, control.step]


def require_family(model: str) -> XiaomiModel:
    """Return the installed family for a model id."""
    family = resolve_family(model)
    assert family is not None
    return family


def connect_device(name: str) -> DreameVacuumDevice:
    """Connect one loopback device and return it after the handshake."""
    device = DreameVacuumDevice(
        name,
        LOOPBACK_HOST,
        LOOPBACK_TOKEN,
        LOOPBACK_MAC,
        account_type="mi",
        family_resolver=resolve_family,
    )
    device.connect_device()
    return device


def assert_traffic_is_mapped(fake: FakeMiio, family: XiaomiModel) -> None:
    """Assert every write and action stayed on a mapped address."""
    allowed = {()}
    for control in family.controls:
        allowed.add(control.action_parameters)
    outside_writes, outside_actions, unexpected = traffic_outside_map(
        fake.writes,
        fake.actions,
        fake.action_inputs,
        set(mapped_addresses(family, "property")),
        set(mapped_addresses(family, "action")),
        allowed,
    )
    assert not outside_writes
    assert not outside_actions
    assert not unexpected


def force_property_set(
    device: DreameVacuumDevice, prop: DreameVacuumProperty, value: object
) -> None:
    """Set a property even when the device already stores that value."""
    current = device.get_property(prop)
    if current == value:
        other: object = 0 if value != 0 else 1
        if prop is DreameVacuumProperty.VOLUME:
            other = 1 if value == 0 else 0
        assert device.set_property(prop, other) is True
    assert device.set_property(prop, value) is True


def send_bool_values(
    device: DreameVacuumDevice,
    fake: FakeMiio,
    prop: DreameVacuumProperty,
    mapping: Mapping[str, int],
) -> None:
    """Write both integer and boolean forms and assert each wire value."""
    for value in (1, 0, True, False):
        force_property_set(device, prop, value)
        assert fake.writes[-1] == (mapping["siid"], mapping["piid"], value)


def assert_spec_is_fully_classified(case: SpecCase) -> None:
    """Assert every spec item is mapped or omitted with one allowed reason."""
    if case.spec_type is not None:
        document = load_spec_document(case.spec_filename)
        assert document["type"] == case.spec_type
    family = require_family(case.model)
    seen: set[tuple[str, int, int]] = set()
    start_custom = 0
    for filename, expected in case.classification_counts.items():
        shift = _unmapped_start_custom_count(filename, family, case)
        start_custom += shift
        assert _classify_file(case, family, filename, seen) == (
            expected[0] - shift,
            expected[1] + shift,
        )
    if case.reason_prefix_counts is not None:
        prefixes = dict(case.reason_prefix_counts)
        if start_custom:
            prefixes["map"] = prefixes.get("map", 0) + start_custom
        assert _reason_prefix_counts(case) == prefixes
    for kind, siid, iid in case.absent_items:
        assert (kind, siid, iid) not in seen
    for siid, iid in case.checked_events:
        assert (
            omission_reason(
                "event",
                siid,
                iid,
                property_reasons=case.property_reasons,
                action_reasons=case.action_reasons,
                service_reasons=case.service_reasons,
            )
            == _EVENT_REASON
        )
    for pair, reason in {**case.property_reasons, **case.action_reasons}.items():
        kind = "property" if pair in case.property_reasons else "action"
        assert reason
        assert (kind, pair[0], pair[1]) in seen
    required_services = (
        _SERVICE_REASONS
        if case.required_service_ids is None
        else case.required_service_ids
    )
    for siid in required_services:
        assert any(item[1] == siid for item in seen)


def assert_controls_have_english_names(case: SpecCase) -> None:
    """Assert each control key and option slug has an English translation."""
    strings = json.loads(_STRINGS.read_text(encoding="utf-8"))
    entities = strings["entity"]
    assert isinstance(entities, dict)
    for control in require_family(case.model).controls:
        domain = entities[str(control.domain)]
        assert isinstance(domain, dict)
        block = domain[control.key]
        assert isinstance(block, dict)
        assert block["name"]
        if not control.options:
            continue
        states = block["state"]
        assert isinstance(states, dict)
        for _value, slug in control.options:
            assert slug in states


def exercise_mapped_property_reads(case: SpecCase) -> None:
    """Read every mapped property sample and keep cleaning strings off the poll."""
    family = require_family(case.model)
    _assert_remote_state_codec(family, case.state_wire_eight)
    specs = _property_specs(case.spec_filename)
    with FakeMiio(case.model) as fake:
        device = connect_device(case.device_name)
        try:
            _assert_device_is_quiet(device, fake, case.model)
            _read_each_mapped_property(device, fake, family, specs)
            _assert_cleaning_properties_are_not_polled(device, family)
        finally:
            release_device(device)
        assert_traffic_is_mapped(fake, family)


def exercise_writable_values(case: SpecCase) -> None:
    """Send every writable sample and refuse a property this model does not map."""
    family = require_family(case.model)
    specs = _property_specs(case.spec_filename)
    with FakeMiio(case.model) as fake:
        device = connect_device(case.device_name)
        try:
            _send_each_writable_value(device, fake, family, specs)
            _assert_volume_span_and_blocked_map(device, fake, family)
        finally:
            release_device(device)
        assert_traffic_is_mapped(fake, family)


def exercise_mapped_actions(case: SpecCase) -> None:
    """Invoke every mapped action and refuse actions that need parameters."""
    family = require_family(case.model)
    _assert_mapped_actions_take_no_input(case, family)
    with FakeMiio(case.model) as fake:
        device = connect_device(case.device_name)
        try:
            _invoke_each_mapped_action(device, fake, family)
            _refuse_parameterized_actions(device, fake)
        finally:
            release_device(device)
        assert_traffic_is_mapped(fake, family)
        expected = {
            (item["siid"], item["aiid"]) for item in family.action_overrides.values()
        }
        auto_empty = family.action_overrides.get("START_AUTO_EMPTY")
        if auto_empty is not None:
            expected.discard((auto_empty["siid"], auto_empty["aiid"]))
        assert set(fake.actions) == expected


def exercise_status_wires(case: SpecCase) -> None:
    """Drive every published status wire through the shell state machine."""
    family = require_family(case.model)
    state = family.property_overrides["STATE"]
    charging = family.property_overrides.get("CHARGING_STATUS", {})
    error = family.property_overrides["ERROR"]
    with FakeMiio(case.model) as fake:
        device = connect_device(case.device_name)
        try:
            _assert_each_status_wire(device, fake, case, state, charging, error)
            if case.station_shell:
                _assert_shell_transitions(device, fake, family, state, charging, error)
            else:
                _assert_sweep_shell_transitions(device, fake, family)
        finally:
            release_device(device)
        assert_traffic_is_mapped(fake, family)


def assert_controls_match_spec(case: SpecCase) -> None:
    """Assert each control's options, range, and access follow its spec item."""
    family = require_family(case.model)
    current = spec_index(case.spec_filename)
    previous = (
        None
        if case.previous_spec_filename is None
        else spec_index(case.previous_spec_filename)
    )
    keys = [control.key for control in family.controls]
    assert len(keys) == len(set(keys))
    for control in family.controls:
        _assert_one_control(case, family, control, current, previous)


def exercise_control_values(case: SpecCase) -> None:
    """Read every control sample and send every writable value, including 0-255."""
    family = require_family(case.model)
    specs = spec_index(case.spec_filename)
    with FakeMiio(case.model) as fake:
        device = connect_device(case.device_name)
        try:
            device._request_properties()
            for control in family.controls:
                _exercise_one_control(device, fake, family, specs, control)
        finally:
            release_device(device)
        assert_traffic_is_mapped(fake, family)


def exercise_rejected_control_traffic(case: SpecCase) -> None:
    """Assert a refused read or write leaves the stored value unchanged."""
    family = require_family(case.model)
    alarm = next(
        (
            item
            for item in family.controls
            if item.key == "xiaomi_alarm" and item.piid is not None
        ),
        None,
    )
    if alarm is None:
        alarm = next(
            item for item in family.controls if item.writable and item.piid is not None
        )
    button = next(item for item in family.controls if item.aiid is not None)
    with FakeMiio(case.model) as fake:
        device = connect_device(case.device_name)
        try:
            before = read_control(device, alarm)
            writes = len(fake.writes)
            actions = len(fake.actions)
            device._protocol.set_property = _refuse_write
            with pytest.raises(XiaomiControlException):
                write_control(device, alarm, True)
            assert read_control(device, alarm) == before
            device._protocol.action = _refuse_action
            with pytest.raises(XiaomiControlException):
                invoke_control(device, button)
            device._protocol.get_properties = _refuse_read
            family.refresh_controls(device)
            assert read_control(device, alarm) == before
            assert len(fake.writes) == writes
            assert len(fake.actions) == actions
        finally:
            release_device(device)


def _property_specs(filename: str) -> dict[tuple[int, int], dict[str, object]]:
    """Index property items by siid and piid."""
    return {
        (siid, iid): spec
        for kind, siid, iid, spec in spec_items(filename)
        if kind == "property"
    }


def _unmapped_start_custom_count(
    filename: str, family: XiaomiModel, case: SpecCase
) -> int:
    """Count start-custom actions this change leaves unmapped on purpose."""
    mapped = mapped_addresses(family, "action")
    count = 0
    for kind, siid, iid, _spec in spec_items(filename):
        if kind != "action" or (siid, iid) not in _START_CUSTOM_ACTIONS:
            continue
        if (siid, iid) in mapped or (siid, iid) in case.action_reasons:
            continue
        count += 1
    return count


def _classify_file(
    case: SpecCase,
    family: XiaomiModel,
    filename: str,
    seen: set[tuple[str, int, int]],
) -> tuple[int, int]:
    """Classify one spec file and return its mapped and omitted counts."""
    mapped_count = 0
    omitted_count = 0
    for kind, siid, iid, _spec in spec_items(filename):
        seen.add((kind, siid, iid))
        mapped = (
            (siid, iid) in mapped_addresses(family, kind) if kind != "event" else False
        )
        reason = omission_reason(
            kind,
            siid,
            iid,
            property_reasons=case.property_reasons,
            action_reasons=case.action_reasons,
            service_reasons=case.service_reasons,
        )
        services = (
            _SERVICE_REASONS if case.service_reasons is None else case.service_reasons
        )
        # One mapped property may live in a service the rest of which stays omitted.
        if mapped and reason is not None and reason == services.get(siid):
            reason = None
        assert mapped != bool(reason), (filename, kind, siid, iid, reason)
        if reason:
            assert reason.startswith(_REASON_PREFIXES), reason
            omitted_count += 1
        if mapped:
            name = mapped_addresses(family, kind)[(siid, iid)]
            published = _has_published_name(_spec)
            version_only = (siid, iid) in case.version_only_controls
            assert published or version_only
            assert name
            mapped_count += 1
    return mapped_count, omitted_count


def _has_published_name(spec: Mapping[str, object]) -> bool:
    """Return whether the item, or every value it lists, has a description."""
    if spec.get("description"):
        return True
    # Sweep-family items name the property in the URN and leave description blank.
    urn = spec.get("type")
    if isinstance(urn, str):
        parts = urn.split(":")
        if len(parts) >= 4 and parts[3]:
            return True
    # Custom services name each value and leave the property description empty.
    listed = spec.get("value-list")
    if not isinstance(listed, list) or not listed:
        return False
    return all(isinstance(item, dict) and item.get("description") for item in listed)


def _reason_prefix_counts(case: SpecCase) -> dict[str, int]:
    """Count omission-reason prefixes across the case's spec files."""
    prefixes: dict[str, int] = {}
    for filename in case.classification_counts:
        for kind, siid, iid, _spec in spec_items(filename):
            reason = omission_reason(
                kind,
                siid,
                iid,
                property_reasons=case.property_reasons,
                action_reasons=case.action_reasons,
                service_reasons=case.service_reasons,
            )
            if not reason:
                continue
            prefix = reason.split(":", 1)[0]
            prefixes[prefix] = prefixes.get(prefix, 0) + 1
    return prefixes


def _assert_remote_state_codec(family: XiaomiModel, wire_eight: int | None) -> None:
    """Assert wire 8 is remote control on X20 Max and the caller's own code."""
    x20 = resolve_family(MODEL_X20_MAX)
    vacuum_5 = resolve_family(MODEL_ROBOT_VACUUM_5)
    assert x20 is not None
    assert vacuum_5 is not None
    assert x20.convert_incoming("STATE", 8) == DreameVacuumState.REMOTE_CONTROL
    assert vacuum_5.convert_incoming("STATE", 8) == 19
    if wire_eight is not None:
        assert family.convert_incoming("STATE", 8) == wire_eight


def _assert_device_is_quiet(
    device: DreameVacuumDevice, fake: FakeMiio, model: str
) -> None:
    """Assert the handshake identified the model and sent no commands."""
    assert device.info is not None
    assert device.info.model == model
    assert fake.actions == []
    assert fake.writes == []


def _read_each_mapped_property(
    device: DreameVacuumDevice,
    fake: FakeMiio,
    family: XiaomiModel,
    specs: Mapping[tuple[int, int], Mapping[str, object]],
) -> None:
    """Read or push every sample and assert the converted property value."""
    for name, mapping in family.property_overrides.items():
        prop = DreameVacuumProperty[name]
        address = (mapping["siid"], mapping["piid"])
        for sample in spec_samples(specs[address]):
            if prop is DreameVacuumProperty.CLEANING_PROPERTIES:
                # The shell never polls this string. A pushed value still converts.
                device._handle_properties(
                    [
                        {
                            "did": str(prop.value),
                            "siid": address[0],
                            "piid": address[1],
                            "code": 0,
                            "value": sample,
                        }
                    ]
                )
            else:
                fake.set_value(address[0], address[1], sample)
                device._request_properties([prop])
            assert device.get_property(prop) == family.convert_incoming(name, sample)


def _assert_cleaning_properties_are_not_polled(
    device: DreameVacuumDevice, family: XiaomiModel
) -> None:
    """Assert a full poll skips the cleaning-properties string."""
    requested: list[tuple[int, int]] = []

    def record(
        parameters: list[dict[str, int]],
        retry_count: int = 1,
        timeout: object = None,
    ) -> list[dict[str, object]]:
        del retry_count, timeout
        requested.extend((item["siid"], item["piid"]) for item in parameters)
        return [
            {
                "did": item["did"],
                "siid": item["siid"],
                "piid": item["piid"],
                "code": 0,
                "value": 0,
            }
            for item in parameters
        ]

    device._protocol.get_properties = record
    device._request_properties()
    cleaning = family.property_overrides.get("CLEANING_PROPERTIES")
    if cleaning is not None:
        assert (cleaning["siid"], cleaning["piid"]) not in requested
    assert device.capability.new_state is False


def _send_each_writable_value(
    device: DreameVacuumDevice,
    fake: FakeMiio,
    family: XiaomiModel,
    specs: Mapping[tuple[int, int], Mapping[str, object]],
) -> None:
    """Send every writable sample, expanding ranges of at most 100 steps."""
    for name, mapping in family.property_overrides.items():
        spec = specs[(mapping["siid"], mapping["piid"])]
        access = spec.get("access")
        assert isinstance(access, list)
        if "write" not in access:
            continue
        prop = DreameVacuumProperty[name]
        if spec.get("format") == "bool":
            send_bool_values(device, fake, prop, mapping)
            continue
        if name in {"STATE", "TASK_STATUS"}:
            samples = _write_samples(spec)
            assert samples
            before = len(fake.writes)
            stored = family.convert_incoming(name, samples[0])
            with pytest.raises(DeviceException):
                force_property_set(device, prop, stored)
            assert len(fake.writes) == before
            continue
        for sample in _write_samples(spec):
            stored = family.convert_incoming(name, sample)
            force_property_set(device, prop, stored)
            assert fake.writes[-1][0] == mapping["siid"]
            assert fake.writes[-1][1] == mapping["piid"]
            assert fake.writes[-1][2] == family.convert_outgoing(name, stored)


def _assert_volume_span_and_blocked_map(
    device: DreameVacuumDevice, fake: FakeMiio, family: XiaomiModel
) -> None:
    """Assert volume covered its Dreame span and map data produced no write."""
    if "VOLUME" not in family.property_overrides:
        before = len(fake.writes)
        assert device.set_property(DreameVacuumProperty.MAP_DATA, "blocked") is False
        assert len(fake.writes) == before
        return
    sent_volume = {
        value
        for siid, piid, value in fake.writes
        if (siid, piid)
        == (
            family.property_overrides["VOLUME"]["siid"],
            family.property_overrides["VOLUME"]["piid"],
        )
    }
    assert sent_volume == set(range(101))
    before = len(fake.writes)
    assert device.set_property(DreameVacuumProperty.MAP_DATA, "blocked") is False
    assert len(fake.writes) == before


def _action_filenames(case: SpecCase) -> tuple[str, ...]:
    """Return the spec files whose mapped actions must take no parameters."""
    if case.action_spec_filenames:
        return case.action_spec_filenames
    return (case.spec_filename,)


def _assert_mapped_actions_take_no_input(case: SpecCase, family: XiaomiModel) -> None:
    """Assert every Dreame-mapped action spec accepts an empty parameter list."""
    dreame_actions = {
        (item["siid"], item["aiid"]) for item in family.action_overrides.values()
    }
    for filename in _action_filenames(case):
        for kind, siid, iid, spec in spec_items(filename):
            if kind == "action" and (siid, iid) in dreame_actions:
                assert not spec.get("in"), (filename, siid, iid)


def _invoke_each_mapped_action(
    device: DreameVacuumDevice, fake: FakeMiio, family: XiaomiModel
) -> None:
    """Call every mapped action, and expect auto-empty to stay unavailable."""
    for name in family.action_overrides:
        action = DreameVacuumAction[name]
        before = len(fake.actions)
        if name == "START_AUTO_EMPTY":
            with pytest.raises(UnavailableException):
                device.call_action(action)
            assert len(fake.actions) == before
            continue
        result = device.call_action(action)
        assert result is not None
        assert result.get("code") == 0
        assert len(fake.actions) == before + 1
        assert fake.action_inputs[-1] == []


def _refuse_parameterized_actions(device: DreameVacuumDevice, fake: FakeMiio) -> None:
    """Assert Dreame actions that need parameters are not sent."""
    for action in _REFUSED_ACTIONS:
        before = len(fake.actions)
        with pytest.raises(InvalidActionException):
            device.call_action(action, {"in": [1]})
        assert len(fake.actions) == before


def _assert_each_status_wire(
    device: DreameVacuumDevice,
    fake: FakeMiio,
    case: SpecCase,
    state: Mapping[str, int],
    charging: Mapping[str, int],
    error: Mapping[str, int],
) -> None:
    """Assert each published status wire becomes the expected shell state."""
    for wire, expected in case.state_after_read.items():
        if charging:
            fake.set_value(charging["siid"], charging["piid"], 2)
        fake.set_value(error["siid"], error["piid"], 0)
        fake.set_value(state["siid"], state["piid"], wire)
        requested = [DreameVacuumProperty.STATE, DreameVacuumProperty.ERROR]
        if charging:
            requested.append(DreameVacuumProperty.CHARGING_STATUS)
        device._request_properties(requested)
        assert device.status.state is expected, wire


def _assert_shell_transitions(
    device: DreameVacuumDevice,
    fake: FakeMiio,
    family: XiaomiModel,
    state: Mapping[str, int],
    charging: Mapping[str, int],
    error: Mapping[str, int],
) -> None:
    """Assert dock, idle, start, pause, resume, return, and error transitions."""
    fake.set_value(charging["siid"], charging["piid"], 1)
    fake.set_value(state["siid"], state["piid"], 2)
    device._request_properties(
        [DreameVacuumProperty.STATE, DreameVacuumProperty.CHARGING_STATUS]
    )
    assert device.status.docked is True
    assert device.status.state is DreameVacuumState.CHARGING
    fake.set_value(charging["siid"], charging["piid"], 2)
    fake.set_value(state["siid"], state["piid"], 1)
    device._request_properties(
        [DreameVacuumProperty.STATE, DreameVacuumProperty.CHARGING_STATUS]
    )
    assert device.status.state is DreameVacuumState.IDLE
    device.start()
    device._request_properties([DreameVacuumProperty.STATE])
    assert device.status.state is DreameVacuumState.SWEEPING
    device.pause()
    device._request_properties([DreameVacuumProperty.STATE])
    assert device.status.state is DreameVacuumState.PAUSED
    device.start()
    device._request_properties([DreameVacuumProperty.STATE])
    assert device.status.state is DreameVacuumState.SWEEPING
    assert fake.actions[-1] == (
        family.action_overrides["RESUME"]["siid"],
        family.action_overrides["RESUME"]["aiid"],
    )
    device.return_to_base()
    device._request_properties(
        [DreameVacuumProperty.STATE, DreameVacuumProperty.CHARGING_STATUS]
    )
    assert device.status.state is DreameVacuumState.CHARGING
    fake.set_value(error["siid"], error["piid"], 1)
    fake.set_value(charging["siid"], charging["piid"], 2)
    fake.set_value(state["siid"], state["piid"], 1)
    device._request_properties(
        [
            DreameVacuumProperty.ERROR,
            DreameVacuumProperty.STATE,
            DreameVacuumProperty.CHARGING_STATUS,
        ]
    )
    assert device.status.state is DreameVacuumState.ERROR


def _assert_sweep_shell_transitions(
    device: DreameVacuumDevice,
    fake: FakeMiio,
    family: XiaomiModel,
) -> None:
    """Assert idle, start, stop, return, and error when charging status is unmapped."""
    state = family.property_overrides["STATE"]
    error = family.property_overrides["ERROR"]
    returning = wire_for_state(family, StoredState.RETURNING)
    fake.set_value(error["siid"], error["piid"], 0)
    fake.set_value(state["siid"], state["piid"], 1)
    device._request_properties([DreameVacuumProperty.STATE, DreameVacuumProperty.ERROR])
    assert device.status.state is DreameVacuumState.IDLE
    device.start()
    device._request_properties([DreameVacuumProperty.STATE])
    assert device.status.state is DreameVacuumState.SWEEPING
    if "PAUSE" in family.action_overrides:
        device.pause()
        device._request_properties([DreameVacuumProperty.STATE])
        assert device.status.state is DreameVacuumState.PAUSED
        device.start()
        device._request_properties([DreameVacuumProperty.STATE])
        assert device.status.state is DreameVacuumState.SWEEPING
        assert fake.actions[-1] == (
            family.action_overrides["RESUME"]["siid"],
            family.action_overrides["RESUME"]["aiid"],
        )
    else:
        before = len(fake.actions)
        with pytest.raises(InvalidActionException):
            device.pause()
        assert len(fake.actions) == before
        device._request_properties([DreameVacuumProperty.STATE])
        assert device.status.state is DreameVacuumState.SWEEPING
        device.start()
        assert fake.actions[-1] == (
            family.action_overrides["START"]["siid"],
            family.action_overrides["START"]["aiid"],
        )
    device.stop()
    assert fake.actions[-1] == (
        family.action_overrides["STOP"]["siid"],
        family.action_overrides["STOP"]["aiid"],
    )
    fake.set_value(state["siid"], state["piid"], returning)
    device._request_properties([DreameVacuumProperty.STATE])
    assert device.status.state is DreameVacuumState.RETURNING
    device.return_to_base()
    device._request_properties([DreameVacuumProperty.STATE])
    assert device.status.state is DreameVacuumState.CHARGING
    fake.set_value(error["siid"], error["piid"], 1)
    fake.set_value(state["siid"], state["piid"], 1)
    device._request_properties([DreameVacuumProperty.ERROR, DreameVacuumProperty.STATE])
    assert device.status.state is DreameVacuumState.ERROR
    if "LOCATE" not in family.action_overrides:
        return
    device.locate()
    assert fake.actions[-1] == (
        family.action_overrides["LOCATE"]["siid"],
        family.action_overrides["LOCATE"]["aiid"],
    )


def _assert_one_control(
    case: SpecCase,
    family: XiaomiModel,
    control: XiaomiControl,
    current: Mapping[tuple[str, int, int], Mapping[str, object]],
    previous: Mapping[tuple[str, int, int], Mapping[str, object]] | None,
) -> None:
    """Assert one control against the current spec and, when present, the previous."""
    if control.property_name:
        spec = current[("property", *property_address(family, control.property_name))]
        assert_control_options(control, spec)
        return
    kind = "action" if control.aiid is not None else "property"
    pair = (
        control.siid,
        control.aiid if control.aiid is not None else control.piid,
    )
    assert (kind, pair[0], pair[1]) in current
    assert_control_matches_spec(control, current[(kind, pair[0], pair[1])])
    for piid, value in control.action_parameters:
        listed = current[("property", control.siid, piid)].get("value-list")
        assert isinstance(listed, list)
        published = {item["value"] for item in listed if isinstance(item, dict)}
        assert value in published
    if previous is None:
        return
    qualified = (kind, pair[0], pair[1])
    if qualified in case.version_only_items or pair in case.version_only_controls:
        assert qualified not in previous
        return
    assert_control_matches_spec(control, previous[qualified])


def _exercise_one_control(
    device: DreameVacuumDevice,
    fake: FakeMiio,
    family: XiaomiModel,
    specs: Mapping[tuple[str, int, int], Mapping[str, object]],
    control: XiaomiControl,
) -> None:
    """Read and, when writable, send every sample for one control."""
    if control.aiid is not None:
        spec = specs[("action", control.siid, control.aiid)]
        assert list(spec.get("in") or []) == [
            piid for piid, _value in control.action_parameters
        ]
        invoke_control(device, control)
        assert fake.actions[-1] == (control.siid, control.aiid)
        assert fake.action_inputs[-1] == [
            {"piid": piid, "value": value} for piid, value in control.action_parameters
        ]
        return
    if control.property_name:
        _send_named_property_options(device, fake, family, control)
        return
    direct = specs[("property", control.siid, control.piid)]
    if control.readable:
        for sample in spec_samples(direct, full_range_limit=_CONTROL_SAMPLE_LIMIT):
            fake.set_value(control.siid, control.piid, sample)
            family.refresh_controls(device)
            assert read_control(device, control) == sample
    if not control.writable:
        return
    for sample in spec_samples(direct, full_range_limit=_CONTROL_SAMPLE_LIMIT):
        write_control(device, control, sample)
        assert fake.writes[-1] == (control.siid, control.piid, sample)
        assert read_control(device, control) == sample


def _write_samples(spec: Mapping[str, object]) -> list[object]:
    """Return writable samples, expanding a range before the generic samples."""
    bounds = _range_bounds(spec)
    if bounds is not None:
        start, end, step = bounds
        if (end - start) // step <= _WRITE_SAMPLE_LIMIT:
            return list(range(start, end + 1, step))
    return spec_samples(spec)


def _range_bounds(spec: Mapping[str, object]) -> tuple[int, int, int] | None:
    """Return start, end, and step when the spec publishes a three-item range."""
    bounds = spec.get("value-range")
    if not isinstance(bounds, list) or len(bounds) != 3:
        return None
    start, end, step = bounds
    assert isinstance(start, int)
    assert isinstance(end, int)
    assert isinstance(step, int)
    return start, end, step


def _send_named_property_options(
    device: DreameVacuumDevice,
    fake: FakeMiio,
    family: XiaomiModel,
    control: XiaomiControl,
) -> None:
    """Send each option of a control that reuses a Dreame property."""
    name = control.property_name
    assert name
    prop = DreameVacuumProperty[name]
    mapping = family.property_overrides[name]
    for value, _slug in control.options:
        force_property_set(device, prop, value)
        assert fake.writes[-1] == (mapping["siid"], mapping["piid"], value)


def _refuse_write(*_args: object, **_kwargs: object) -> list[dict[str, int]]:
    return [{"code": -1}]


def _refuse_action(*_args: object, **_kwargs: object) -> dict[str, int]:
    return {"code": -1}


def _refuse_read(*_args: object, **_kwargs: object) -> None:
    return None

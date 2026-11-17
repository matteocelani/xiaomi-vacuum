"""Guards for property values that are not the strings Dreame parsers expect."""

from __future__ import annotations

import json
from types import SimpleNamespace

from custom_components.xiaomi_robot_vacuum.dreame.device import (
    DreameVacuumDevice,
    DreameVacuumDeviceStatus,
    _is_positive_value,
)
from custom_components.xiaomi_robot_vacuum.dreame.protocol import (
    DreameVacuumDeviceProtocol,
    DreameVacuumDreameHomeCloudProtocol,
)
from custom_components.xiaomi_robot_vacuum.dreame.types import (
    DreameVacuumProperty,
    DreameVacuumStreamStatus,
)

_FAKE_TOKEN = "00" * 16


def _device(values: dict[DreameVacuumProperty, object]) -> DreameVacuumDevice:
    device = object.__new__(DreameVacuumDevice)
    device.data = {prop.value: value for prop, value in values.items()}
    device.status = SimpleNamespace(
        schedule=None,
        dnd_tasks=None,
        stream_session=None,
        stream_status=None,
        off_peak_charging_config=None,
    )
    return device


def _status(value: object) -> DreameVacuumDeviceStatus:
    status = object.__new__(DreameVacuumDeviceStatus)
    status._device = SimpleNamespace(get_property=lambda _prop: value)
    return status


def _cloud() -> SimpleNamespace:
    strings = [f"k{index}" for index in range(31)]
    strings[7] = "uid"
    strings[8] = "host"
    strings[9] = "prop"
    strings[10] = "stream"
    strings[30] = "model"
    return SimpleNamespace(_strings=strings, _stream_key=None)


def _device_info(prop: object) -> dict[str, object]:
    return {
        "uid": "user",
        "did": "device",
        "model": "xiaomi.vacuum.d109gl",
        "host": "127.0.0.1",
        "prop": prop,
    }


def test_schedule_ignores_a_non_string_order_clean_value():
    for value in (19, {"order": "clean"}):
        device = _device({DreameVacuumProperty.SCHEDULE: value})
        DreameVacuumDevice._schedule_changed(device)
        assert device.status.schedule == []


def test_schedule_still_parses_a_dreame_string():
    device = _device({DreameVacuumProperty.SCHEDULE: "1-1-08:00-1111111-1-0-1-2-0"})
    DreameVacuumDevice._schedule_changed(device)
    assert len(device.status.schedule) == 1
    task = device.status.schedule[0]
    assert task.id == 1
    assert task.enabled is True
    assert task.time == "08:00"


def test_dnd_ignores_a_non_string_value_and_parses_json():
    skipped = _device({DreameVacuumProperty.DND_TASK: 1})
    DreameVacuumDevice._dnd_task_changed(skipped)
    assert skipped.status.dnd_tasks == []
    raw = json.dumps(
        [{"id": 2, "en": True, "st": "22:00", "et": "07:00", "wk": 127, "ss": 0}]
    )
    parsed = _device({DreameVacuumProperty.DND_TASK: raw})
    DreameVacuumDevice._dnd_task_changed(parsed)
    assert parsed.status.dnd_tasks[0].id == 2
    assert parsed.status.dnd_tasks[0].start == "22:00"


def test_stream_status_ignores_a_non_string_value_and_parses_json():
    skipped = _device({DreameVacuumProperty.STREAM_STATUS: 1})
    DreameVacuumDevice._stream_status_changed(skipped)
    assert skipped.status.stream_session is None
    raw = json.dumps(
        {"result": 0, "session": "s", "operType": "end", "operation": "end"}
    )
    parsed = _device({DreameVacuumProperty.STREAM_STATUS: raw})
    DreameVacuumDevice._stream_status_changed(parsed)
    assert parsed.status.stream_session == "s"
    assert parsed.status.stream_status is DreameVacuumStreamStatus.IDLE


def test_off_peak_charging_ignores_a_non_string_value_and_parses_json():
    skipped = _device({DreameVacuumProperty.OFF_PEAK_CHARGING: 1})
    DreameVacuumDevice._off_peak_charging_changed(skipped)
    assert skipped.status.off_peak_charging_config is None
    raw = json.dumps({"enable": True, "startTime": "22:00", "endTime": "08:00"})
    parsed = _device({DreameVacuumProperty.OFF_PEAK_CHARGING: raw})
    DreameVacuumDevice._off_peak_charging_changed(parsed)
    assert parsed.status.off_peak_charging_config["startTime"] == "22:00"


def test_cleaning_paused_reads_numeric_strings_and_leaves_integers():
    assert _status("0").cleaning_paused is False
    assert _status("1").cleaning_paused is True
    assert _status("paused").cleaning_paused is False
    assert _status(0).cleaning_paused is False
    assert _status(1).cleaning_paused is True
    assert _status(2).cleaning_paused is True
    assert _status(True).cleaning_paused is True
    assert _status(False).cleaning_paused is False
    assert _status(None).cleaning_paused is False


def test_cleaning_history_accepts_a_string_count_and_a_missing_count(caplog):
    calls: list[tuple[object, object, object]] = []

    def get_device_event(did: object, limit: object, start: object) -> None:
        calls.append((did, limit, start))

    def run(count: object) -> None:
        calls.clear()
        device = object.__new__(DreameVacuumDevice)
        device.data = {}
        if count is not None:
            device.data[DreameVacuumProperty.CLEANING_COUNT.value] = count
        device.property_mapping = {}
        device._cleaning_history_update = -1
        device._protocol = SimpleNamespace(
            cloud=SimpleNamespace(connected=True, get_device_event=get_device_event),
            prefer_cloud=False,
            connected=True,
        )
        device.status = SimpleNamespace(_cleaning_history=None, task_status=None)
        device.capability = SimpleNamespace(cruising=False)
        DreameVacuumDevice._request_cleaning_history(device)

    run("4")
    assert calls
    assert calls[0][1] == 34
    run(None)
    assert calls
    assert calls[0][1] == 35
    run({"n": 1})
    assert "Get Cleaning History failed" in caplog.text


def test_positive_flag_accepts_numeric_strings():
    assert _is_positive_value("2") is True
    assert _is_positive_value("0") is False
    assert _is_positive_value("no") is True
    assert _is_positive_value(0) is False
    assert _is_positive_value(3) is True
    assert _is_positive_value(True) is True
    assert _is_positive_value(False) is False
    assert _is_positive_value(0.5) is True
    assert _is_positive_value(0.0) is False


def test_device_info_ignores_a_non_string_prop_and_reads_a_string_prop():
    skipped = _cloud()
    DreameVacuumDreameHomeCloudProtocol._handle_device_info(skipped, _device_info(19))
    assert skipped._stream_key is None
    assert skipped._host == "127.0.0.1"
    parsed = _cloud()
    DreameVacuumDreameHomeCloudProtocol._handle_device_info(
        parsed, _device_info(json.dumps({"stream": "session-key"}))
    )
    assert parsed._stream_key == "session-key"


def test_shared_miio_timeout_stays_two_seconds():
    protocol = DreameVacuumDeviceProtocol("127.0.0.1", _FAKE_TOKEN)
    assert protocol._timeout == 2

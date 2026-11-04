"""Regression tests for the fail-closed review findings."""

from __future__ import annotations

import base64
import gzip
import json
from types import SimpleNamespace

from custom_components.dreame_vacuum.dreame.catalog import (
    catalog_supports_model,
    load_model_catalog,
)
from custom_components.dreame_vacuum.dreame.device import DreameVacuumDevice
from custom_components.dreame_vacuum.dreame.exceptions import (
    DeviceException,
    InvalidActionException,
    InvalidValueException,
    NotSupportedException,
)
from custom_components.dreame_vacuum.dreame.protocol import DreameVacuumProtocol
from custom_components.dreame_vacuum.dreame.types import (
    DreameVacuumAction,
    DreameVacuumActionMapping,
    DreameVacuumCarpetCleaning,
    DreameVacuumDeviceCapability,
    DreameVacuumProperty,
    DreameVacuumPropertyMapping,
    DreameVacuumStatus,
)
from custom_components.dreame_vacuum.xiaomi import resolve_family
from custom_components.dreame_vacuum.xiaomi.controls import (
    ControlDomain,
    ValueKind,
    XiaomiControl,
    refresh_controls,
    write_control,
)
from custom_components.dreame_vacuum.xiaomi.exceptions import (
    XiaomiControlException,
    XiaomiValueException,
)
from custom_components.dreame_vacuum.xiaomi.mapping import MODEL_S20_PLUS, MODEL_X20_MAX
from custom_components.dreame_vacuum.xiaomi.value_limits import (
    is_uint8_address,
    wire_allowed,
)
import pytest


def test_start_custom_raises_when_status_is_not_mapped() -> None:
    device = object.__new__(DreameVacuumDevice)
    device.capability = SimpleNamespace(cruising=True)
    device.status = SimpleNamespace(fast_mapping=False)
    device.property_mapping = {}
    device.action_mapping = {DreameVacuumAction.START_CUSTOM: {"siid": 2, "aiid": 9}}
    sent: list[object] = []
    device._protocol = SimpleNamespace(
        action=lambda *_args, **_kwargs: sent.append(True)
    )

    with pytest.raises(InvalidActionException):
        device.start_custom(DreameVacuumStatus.FAST_MAPPING.value, "{}")
    assert sent == []


def _recording_action(sent: list[object]) -> object:
    def record(*_args: object, **_kwargs: object) -> bool:
        sent.append(True)
        return True

    return record


def test_no_xiaomi_family_exposes_start_custom_or_a_null_piid() -> None:
    from custom_components.dreame_vacuum.xiaomi.mapping import _FAMILIES

    assert _FAMILIES
    for model, family in _FAMILIES.items():
        assert "START_CUSTOM" not in family.action_overrides, model
        assert "STATUS" not in family.property_overrides, model
        device = object.__new__(DreameVacuumDevice)
        device.capability = SimpleNamespace(cruising=True)
        device.status = SimpleNamespace(fast_mapping=False)
        device.property_mapping = {
            DreameVacuumProperty[name]: dict(address)
            for name, address in family.property_overrides.items()
        }
        device.action_mapping = {
            DreameVacuumAction[name]: dict(address)
            for name, address in family.action_overrides.items()
            if "siid" in address and "aiid" in address
        }
        sent: list[object] = []
        device._protocol = SimpleNamespace(action=_recording_action(sent))
        with pytest.raises((InvalidActionException, NotSupportedException)):
            device.clean_zone([[1, 2, 3, 4]], 1, "", "")
        assert sent == [], model


def test_dreame_start_custom_still_sends_mapped_piids() -> None:
    device = object.__new__(DreameVacuumDevice)
    device.capability = SimpleNamespace(cruising=True)
    device.status = SimpleNamespace(fast_mapping=False, draining_complete=False)
    device.property_mapping = DreameVacuumPropertyMapping
    device.action_mapping = DreameVacuumActionMapping
    device._property_codec = None
    device._commands_fail_closed = False
    device.schedule_update = lambda *_args, **_kwargs: None
    device._consumable_change = False
    device._map_select_time = None
    device._map_manager = None
    device._property_changed = lambda *_args, **_kwargs: None
    captured: list[object] = []

    def action(siid: int, aiid: int, parameters: object = None, retry_count: int = 2):
        del retry_count
        captured.append((siid, aiid, parameters))
        return {"code": 0}

    device._protocol = SimpleNamespace(action=action, dreame_cloud=False)
    result = device.start_custom(DreameVacuumStatus.FAST_MAPPING.value)
    assert result == {"code": 0}
    payload = captured[0][2]
    assert isinstance(payload, list)
    assert (
        payload[0]["piid"]
        == DreameVacuumPropertyMapping[DreameVacuumProperty.STATUS]["piid"]
    )
    assert all(item["piid"] is not None for item in payload)


def test_unresolved_xiaomi_model_fails_closed() -> None:
    with pytest.raises(DeviceException, match="unsupported model"):
        DreameVacuumDevice(
            "Sim",
            "127.0.0.1",
            "00" * 16,
            configured_model="xiaomi.vacuum.missing",
            family_resolver=resolve_family,
        )
    with pytest.raises(DeviceException, match="unsupported model"):
        DreameVacuumDevice(
            "Sim",
            "127.0.0.1",
            "00" * 16,
            configured_model="mijia.vacuum.missing",
            family_resolver=resolve_family,
        )


def test_configured_family_is_kept_when_the_robot_reports_another_model() -> None:
    device = DreameVacuumDevice(
        "Sim",
        "",
        "",
        configured_model=MODEL_S20_PLUS,
        family_resolver=resolve_family,
    )
    installed = device.property_mapping[DreameVacuumProperty.STATE]
    device.info = SimpleNamespace(model=MODEL_X20_MAX)
    device._apply_reported_family()
    assert device.property_mapping[DreameVacuumProperty.STATE] == installed
    assert device._property_codec.model == MODEL_S20_PLUS


def test_set_properties_rejects_the_whole_write_when_one_property_is_unmapped() -> None:
    device = object.__new__(DreameVacuumDevice)
    device.schedule_update = lambda *_args, **_kwargs: None
    device.property_mapping = {
        DreameVacuumProperty.VOLUME: {"siid": 4, "piid": 2},
    }
    device._property_codec = SimpleNamespace(
        convert_outgoing=lambda name, value: value + 1 if name == "VOLUME" else value
    )
    sent: list[object] = []
    device._protocol = SimpleNamespace(
        set_properties=lambda values: sent.append(values) or [{"code": 0}]
    )

    with pytest.raises(InvalidValueException):
        device.set_properties(
            {
                DreameVacuumProperty.VOLUME: 3,
                DreameVacuumProperty.CARPET_RECOGNITION: 1,
            }
        )
    assert sent == []


def test_set_properties_converts_every_value_for_a_xiaomi_codec() -> None:
    device = object.__new__(DreameVacuumDevice)
    device.schedule_update = lambda *_args, **_kwargs: None
    device.get_property = lambda _prop: None
    device.data = {}
    device._property_update_callback = {}
    device._dirty_data = {}
    device._property_changed = lambda *_args, **_kwargs: None
    device.property_mapping = {
        DreameVacuumProperty.VOLUME: {"siid": 4, "piid": 2},
        DreameVacuumProperty.CLEANING_MODE: {"siid": 2, "piid": 4},
    }
    device._property_codec = SimpleNamespace(
        convert_outgoing=lambda name, value: (
            value + 5 if name == "VOLUME" else value + 1
        )
    )
    sent: list[object] = []
    device._protocol = SimpleNamespace(
        set_properties=lambda values: sent.append(values) or [{"code": 0}]
    )

    assert device.set_properties(
        {
            DreameVacuumProperty.VOLUME: 3,
            DreameVacuumProperty.CLEANING_MODE: 0,
        }
    )
    assert sent == [[(4, 2, 8), (2, 4, 1)]]
    assert device.data[DreameVacuumProperty.VOLUME.value] == 3


def test_dreame_set_properties_still_sends_the_callers_values() -> None:
    device = object.__new__(DreameVacuumDevice)
    device.schedule_update = lambda *_args, **_kwargs: None
    device.get_property = lambda _prop: 1
    device.data = {}
    device._property_update_callback = {}
    device._dirty_data = {}
    device._property_changed = lambda *_args, **_kwargs: None
    device.property_mapping = DreameVacuumPropertyMapping
    device._property_codec = None
    sent: list[object] = []
    device._protocol = SimpleNamespace(
        set_properties=lambda values: sent.append(values) or [{"code": 0}]
    )
    volume = DreameVacuumPropertyMapping[DreameVacuumProperty.VOLUME]
    assert device.set_properties({DreameVacuumProperty.VOLUME: 4})
    assert sent == [[(volume["siid"], volume["piid"], 4)]]


def test_send_async_uses_the_xiaomi_transport_and_does_not_fall_through() -> None:
    protocol = DreameVacuumProtocol()
    seen: list[object] = []

    class _Transport:
        local_auth_failed = False

        def send(
            self, method: str, parameters: object, retry_count: int
        ) -> list[dict[str, int]]:
            del retry_count
            seen.append((method, parameters))
            return [{"code": 0}]

    class _Cloud:
        def send_async(self, *_args: object, **_kwargs: object) -> None:
            raise AssertionError("cloud")

    protocol.property_transport = _Transport()
    protocol.device_cloud = _Cloud()
    protocol.prefer_cloud = True
    protocol.send_async(None, "set_properties", [{"siid": 4, "piid": 2, "value": 1}])
    assert seen == [("set_properties", [{"siid": 4, "piid": 2, "value": 1}])]

    protocol.property_transport = SimpleNamespace(
        local_auth_failed=False, send=lambda *_args, **_kwargs: None
    )
    with pytest.raises(DeviceException):
        protocol.send_async(None, "set_properties", [])


def test_refresh_controls_keeps_going_when_one_read_fails() -> None:
    battery = XiaomiControl(
        key="battery",
        domain=ControlDomain.SENSOR,
        siid=3,
        piid=1,
        value_kind=ValueKind.INT,
    )
    alarm = XiaomiControl(
        key="alarm",
        domain=ControlDomain.SWITCH,
        siid=4,
        piid=1,
        value_kind=ValueKind.BOOL,
    )
    device = SimpleNamespace(
        _xiaomi_values={"battery": 80, "alarm": 1},
        _protocol=SimpleNamespace(
            get_properties=lambda _items: [
                {"siid": 3, "piid": 1, "code": 0, "value": 70},
                {"siid": 4, "piid": 1, "code": -1},
            ]
        ),
    )
    assert refresh_controls(device, (battery, alarm)) is True
    assert device._xiaomi_values["battery"] == 70
    assert "alarm" not in device._xiaomi_values


def test_write_control_rejects_a_value_outside_the_declared_range() -> None:
    control = XiaomiControl(
        key="hours",
        domain=ControlDomain.NUMBER,
        siid=2,
        piid=31,
        writable=True,
        value_kind=ValueKind.INT,
        minimum=1,
        maximum=4,
    )
    sent: list[object] = []
    device = SimpleNamespace(
        _property_codec=None,
        _protocol=SimpleNamespace(
            set_property=lambda *_args: sent.append(True) or [{"code": 0}]
        ),
        _xiaomi_values={},
    )
    with pytest.raises(XiaomiControlException):
        write_control(device, control, 9)
    assert sent == []
    write_control(device, control, 2)
    assert sent == [True]


def test_send_command_rejects_an_unmapped_xiaomi_action() -> None:
    device = object.__new__(DreameVacuumDevice)
    device._property_codec = SimpleNamespace(model=MODEL_S20_PLUS)
    device._commands_fail_closed = False
    device.property_mapping = {DreameVacuumProperty.VOLUME: {"siid": 4, "piid": 2}}
    device.action_mapping = {DreameVacuumAction.START: {"siid": 2, "aiid": 1}}
    device.schedule_update = lambda *_args, **_kwargs: None
    sent: list[object] = []
    device._protocol = SimpleNamespace(send=lambda *_args, **_kwargs: sent.append(True))
    with pytest.raises(InvalidActionException):
        device.send_command("action", {"siid": 14, "aiid": 1})
    assert sent == []
    device.send_command("action", {"siid": 2, "aiid": 1})
    assert sent == [True]


def test_catalog_decode_errors_and_brand_collisions_fail_closed() -> None:
    with pytest.raises(DeviceException):
        load_model_catalog("not-a-catalog")
    payload = json.dumps([[], [], [], {}]).encode()
    blob = base64.b64encode(gzip.compress(payload)).decode("ascii")
    same_suffix = base64.b64encode(
        gzip.compress(
            json.dumps(
                [[[1, 1, 0]], [[[1, 1]]], ["key"], {"shared": 0}],
                separators=(",", ":"),
            ).encode()
        )
    ).decode("ascii")
    assert catalog_supports_model(same_suffix, "xiaomi.vacuum.shared") is True
    assert catalog_supports_model(same_suffix, "mijia.vacuum.shared") is False
    assert catalog_supports_model(blob, "xiaomi.vacuum.shared") is False


def test_wire_limits_allow_published_ranges_and_reject_the_rest() -> None:
    assert wire_allowed(MODEL_S20_PLUS, "VOLUME", 4) is True
    assert wire_allowed(MODEL_S20_PLUS, "VOLUME", 101) is False
    assert wire_allowed(MODEL_S20_PLUS, "SCHEDULE", 1) is False
    assert wire_allowed(MODEL_S20_PLUS, "FAULTS", 1) is False
    assert wire_allowed(MODEL_S20_PLUS, "CLEANING_PROPERTIES", 1) is False
    assert wire_allowed(MODEL_S20_PLUS, "DND", 0) is True
    assert wire_allowed(MODEL_S20_PLUS, "DND", 1) is True
    assert wire_allowed(MODEL_S20_PLUS, "DND", 2) is False
    assert wire_allowed("xiaomi.vacuum.missing", "VOLUME", 1) is False
    assert is_uint8_address("xiaomi.vacuum.missing", 2, 1) is False


def test_outgoing_suction_uses_the_family_offset_and_rejects_unknown_wires() -> None:
    family = resolve_family(MODEL_S20_PLUS)
    assert family is not None
    assert family.convert_outgoing("SUCTION_LEVEL", 2) == 3
    with pytest.raises(XiaomiControlException):
        family.convert_outgoing("SUCTION_LEVEL", 40)
    assert family.convert_incoming("STATE", 99) == -1
    assert family.task_status_code(99, None) == -1
    with pytest.raises(XiaomiValueException):
        family.convert_outgoing("STATE", 1)
    with pytest.raises(XiaomiValueException):
        family.convert_outgoing("TASK_STATUS", 0)


_DREAME_PROTOCOL_XIAOMI: tuple[str, ...] = (
    "xiaomi.vacuum.c102cn",
    "xiaomi.vacuum.c102gl",
    "xiaomi.vacuum.d103cn",
    "xiaomi.vacuum.d110ch",
)


def test_dreame_protocol_xiaomi_models_keep_the_dreame_catalog() -> None:
    for model in _DREAME_PROTOCOL_XIAOMI:
        assert resolve_family(model) is None
        device = DreameVacuumDevice(
            "Sim",
            "",
            "",
            configured_model=model,
            family_resolver=resolve_family,
        )
        assert device.property_mapping is DreameVacuumPropertyMapping
        assert device.action_mapping is DreameVacuumActionMapping
        assert device._property_codec is None
        reported = DreameVacuumDevice("Sim", "", "", family_resolver=resolve_family)
        reported.info = SimpleNamespace(model=model)
        reported._apply_reported_family()
        assert reported.property_mapping is DreameVacuumPropertyMapping
        assert reported._property_codec is None


def test_set_properties_turns_a_codec_error_into_invalid_value() -> None:
    device = object.__new__(DreameVacuumDevice)
    device.schedule_update = lambda *_args, **_kwargs: None
    device.property_mapping = {DreameVacuumProperty.VOLUME: {"siid": 4, "piid": 2}}

    def convert(name: str, value: object) -> object:
        del value
        raise XiaomiValueException(name)

    device._property_codec = SimpleNamespace(convert_outgoing=convert)
    sent: list[object] = []
    device._protocol = SimpleNamespace(
        set_properties=lambda values: sent.append(values) or [{"code": 0}]
    )
    with pytest.raises(InvalidValueException):
        device.set_properties({DreameVacuumProperty.VOLUME: 4})
    assert sent == []


def test_set_carpet_cleaning_skips_properties_the_model_does_not_map() -> None:
    def cleaning_device(mapping: dict[object, dict[str, int]]) -> DreameVacuumDevice:
        device = object.__new__(DreameVacuumDevice)
        device.property_mapping = mapping
        device.status = SimpleNamespace(carpet_recognition=False, auto_mount_mop=False)
        device.capability = SimpleNamespace(
            mop_pad_lifting_plus=False,
            auto_carpet_cleaning=False,
            carpet_crossing=False,
            mop_pad_unmounting=False,
        )
        device.get_property = lambda prop: (
            0 if prop is DreameVacuumProperty.CARPET_CLEANING else None
        )
        return device

    xiaomi = cleaning_device(
        {DreameVacuumProperty.CARPET_CLEANING: {"siid": 2, "piid": 20}}
    )
    captured: list[dict[object, int]] = []
    xiaomi.set_properties = lambda properties: captured.append(dict(properties))
    xiaomi.set_carpet_cleaning(DreameVacuumCarpetCleaning.ADAPTATION)
    assert captured == [
        {DreameVacuumProperty.CARPET_CLEANING: DreameVacuumCarpetCleaning.ADAPTATION}
    ]

    dreame = cleaning_device(DreameVacuumPropertyMapping)
    dreame_captured: list[dict[object, int]] = []
    dreame.set_properties = lambda properties: dreame_captured.append(dict(properties))
    dreame.set_carpet_cleaning(DreameVacuumCarpetCleaning.ADAPTATION)
    assert dreame_captured == [
        {
            DreameVacuumProperty.CARPET_RECOGNITION: 1,
            DreameVacuumProperty.CARPET_CLEANING: DreameVacuumCarpetCleaning.ADAPTATION,
        }
    ]


def test_send_command_rejects_parameters_that_skip_the_allowlist() -> None:
    family = resolve_family(MODEL_S20_PLUS)
    assert family is not None
    device = object.__new__(DreameVacuumDevice)
    device._property_codec = family
    device._commands_fail_closed = False
    device.property_mapping = {
        DreameVacuumProperty[name]: dict(address)
        for name, address in family.property_overrides.items()
    }
    device.action_mapping = {
        DreameVacuumAction[name]: dict(address)
        for name, address in family.action_overrides.items()
        if "siid" in address and "aiid" in address
    }
    device.schedule_update = lambda *_args, **_kwargs: None
    sent: list[object] = []
    device._protocol = SimpleNamespace(
        send=lambda command, parameters, retry_count: (
            sent.append((command, parameters, retry_count)) or {"ok": True}
        )
    )
    with pytest.raises(InvalidActionException):
        device.send_command("set_properties", {"siid": 4, "piid": 2, "value": 4})
    with pytest.raises(InvalidActionException):
        device.send_command("set_properties", [])
    with pytest.raises(InvalidActionException):
        device.send_command("get_properties", [])
    with pytest.raises(InvalidActionException):
        device.send_command(
            "set_properties", [{"siid": 4, "piid": 2, "value": 4, "extra": 1}]
        )
    with pytest.raises(InvalidValueException):
        device.send_command("set_properties", [{"siid": 4, "piid": 2, "value": 101}])
    with pytest.raises(InvalidActionException):
        device.send_command(
            "action", {"siid": 2, "aiid": 1, "in": [{"piid": 99, "value": 1}]}
        )
    with pytest.raises(InvalidValueException):
        device.send_command(
            "action", {"siid": 2, "aiid": 1, "in": [{"piid": 20, "value": 9}]}
        )
    assert sent == []
    device.send_command("set_properties", [{"siid": 4, "piid": 2, "value": 4}])
    assert sent[-1][0] == "set_properties"
    parameters = sent[-1][1]
    assert isinstance(parameters, list)
    assert parameters[0]["value"] == family.convert_outgoing("VOLUME", 4)
    device.send_command(
        "action", {"siid": 2, "aiid": 1, "in": [{"piid": 20, "value": 2}]}
    )
    action_parameters = sent[-1][1]
    assert isinstance(action_parameters, dict)
    assert action_parameters["in"] == [{"piid": 20, "value": 2}]


def test_capability_load_rejects_a_brand_that_does_not_own_the_suffix() -> None:
    device_info = [[[1, 1, 0]], [None], [], {"shared": 0}]
    capability = object.__new__(DreameVacuumDeviceCapability)
    capability._device = SimpleNamespace(
        info=SimpleNamespace(model="mijia.vacuum.shared")
    )
    with pytest.raises(Exception, match="Unsupported Device"):
        capability.load(device_info)
    capability._device = SimpleNamespace(
        info=SimpleNamespace(model="xiaomi.vacuum.shared")
    )
    with pytest.raises(Exception, match="Device capability missing"):
        capability.load(device_info)

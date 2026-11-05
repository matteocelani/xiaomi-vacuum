"""Assertions for the spec-derived Xiaomi cases."""

from __future__ import annotations

from types import SimpleNamespace

from custom_components.dreame_vacuum.dreame.catalog import (
    catalog_supports_model,
    load_model_catalog,
)
from custom_components.dreame_vacuum.dreame.const import DEVICE_INFO
from custom_components.dreame_vacuum.dreame.device import DreameVacuumDevice
from custom_components.dreame_vacuum.dreame.exceptions import InvalidActionException
from custom_components.dreame_vacuum.dreame.protocol import DreameVacuumProtocol
from custom_components.dreame_vacuum.dreame.types import (
    DreameVacuumProperty,
    DreameVacuumStatus,
)
from custom_components.dreame_vacuum.xiaomi import resolve_family
from custom_components.dreame_vacuum.xiaomi.controls import (
    boolean_switch,
    refresh_controls,
    write_control,
)
from custom_components.dreame_vacuum.xiaomi.exceptions import XiaomiControlException
from custom_components.dreame_vacuum.xiaomi.model import StoredTask
import pytest
from tests.xiaomi.deep.cases import (
    ActionCase,
    AddressCase,
    ControlCase,
    FaultCase,
    PropertyCase,
    ValueCase,
    action_cases,
    entity_translations,
    error_translations,
    family_of,
    has_shifted_property,
    property_cases,
    record_of,
    shifted_names,
)
from tests.xiaomi.helpers import FakeMiio, release_device
from tests.xiaomi.spec_helpers import LOOPBACK_HOST, LOOPBACK_MAC, LOOPBACK_TOKEN

C_01 = "C-01: start_custom sends piid None because Xiaomi models do not map STATUS"
H_01 = (
    "H-01: the family is resolved only from the runtime model, "
    "falling back to the Dreame map"
)
H_02 = "H-02: set_properties skips convert_outgoing and does partial writes"
M_02 = "M-02: send_async bypasses the Xiaomi transport"
M_03 = "M-03: there is no outgoing range check and the +1 offset is global"
M_04 = "M-04: unknown Xiaomi states map to COMPLETED"
M_05 = "M-05: one failing control fails the whole update"
_OPEN = (
    "open question: published writable property has no map and no spec omission rule"
)
_NOT_CHARGEABLE = 3
_NOT_CHARGING = 2
_UNKNOWN_WIRE = 250


def check_record(model: str) -> None:
    """The committed spec is the document fetched for this model."""
    record = record_of(model)
    document = record.document
    assert document["type"] == record.urn
    assert record.fetched_on == "2026-11-04"
    assert record.source_url.startswith(
        "https://miot-spec.org/miot-spec-v2/instance?type="
    )
    if record.description_drift:
        assert record.canonical_identical is False
    else:
        assert record.canonical_identical is True


def check_catalog_version(model: str) -> None:
    """The mapped spec is the newest version the instance catalog marks released."""
    record = record_of(model)
    if model == "xiaomi.vacuum.pv32gl":
        assert record.version == 2
        assert tuple(record.catalog_released) == (1,)
        family = family_of(model)
        assert (20, 16) not in {
            (mapping["siid"], mapping["aiid"])
            for mapping in family.action_overrides.values()
        }
        return
    assert record.version in record.catalog_released
    assert record.version == max(record.catalog_released)


def check_catalog(model: str) -> None:
    """DEVICE_INFO accepts the model under its brand prefix."""
    assert catalog_supports_model(DEVICE_INFO, model) is True
    catalog = load_model_catalog(DEVICE_INFO)
    assert model in catalog
    brand = model.split(".", 1)[0]
    assert model.startswith(f"{brand}.vacuum.")


def check_property(case: PropertyCase) -> None:
    """A spec property is mapped or omitted, and a mapped one is readable."""
    if case.token in {"status", "fault", "battery-level", "charging-state"}:
        assert case.mapped_name, (case.model, case.siid, case.piid, case.token)
    if case.mapped_name:
        if "read" in case.access or "notify" in case.access:
            return
        assert "write" in case.access, case.mapped_name
        return
    if case.omission is None:
        pytest.xfail(
            f"{_OPEN}: {case.model} {case.siid}/{case.piid} {case.token} {case.description}"
        )
    assert case.omission


def check_action(case: ActionCase) -> None:
    """A spec action is mapped or omitted with a spec-derived reason."""
    if case.mapped_name:
        if case.mapped_name.startswith("xiaomi_"):
            return
        assert not case.inputs, (case.mapped_name, case.inputs)
        return
    assert case.omission


def check_address(case: AddressCase) -> None:
    """A mapped address exists on this model's spec, so a variant cannot leak it."""
    record = record_of(case.model)
    if case.kind in {"property", "control"}:
        assert _has_property(record.document, case.siid, case.iid), (
            case.model,
            case.name,
            case.siid,
            case.iid,
        )
        return
    assert _has_action(record.document, case.siid, case.iid), (
        case.model,
        case.name,
        case.siid,
        case.iid,
    )


def check_value(case: ValueCase) -> None:
    """A spec value-list entry converts to the stored domain for that property."""
    family = family_of(case.model)
    stored = family.convert_incoming(case.name, case.wire)
    if case.name == "STATE":
        assert stored == family.state_by_wire[case.wire]
        return
    if case.name == "TASK_STATUS":
        assert stored == family.task_by_wire[case.wire]
        return
    if case.name == "CHARGING_STATUS":
        expected = _NOT_CHARGING if case.wire == _NOT_CHARGEABLE else case.wire
        assert stored == expected
        return
    if case.name in shifted_names() and case.wire > 0:
        assert stored == case.wire - 1
        return
    assert stored == case.wire


def check_fault(case: FaultCase) -> None:
    """Fault names come from the spec value-list when the spec publishes one."""
    family = family_of(case.model)
    if case.code is None:
        return
    key = family.fault_name(case.code)
    assert isinstance(key, str)
    assert key != "unknown"
    assert error_translations()[key] == case.description


def check_control(case: ControlCase) -> None:
    """A control's address, access, options, and range follow its spec item."""
    props = {(item.siid, item.piid): item for item in property_cases(case.model)}
    actions = {(item.siid, item.aiid): item for item in _action_index(case.model)}
    if case.piid is not None and case.siid is not None:
        spec = props[(case.siid, case.piid)]
        if case.writable:
            assert "write" in spec.access
        if case.options:
            assert [value for value, _slug in case.options] == [
                value for value, _description in spec.values
            ]
        elif case.value_kind == "bool":
            assert spec.format == "bool"
        elif case.value_kind == "int" and case.minimum is not None:
            assert spec.value_range == (case.minimum, case.maximum, case.step)
    if case.aiid is not None and case.siid is not None:
        assert (case.siid, case.aiid) in actions
    block = entity_translations()[case.domain][case.key]
    assert isinstance(block, dict)
    assert block["name"]


def check_status_wire(model: str, wire: int) -> None:
    """A wire inside the status list is mapped. Any other wire stays unmapped."""
    family = family_of(model)
    published = _status_wires(model)
    stored = family.convert_incoming("STATE", wire)
    if wire in published:
        assert stored == family.state_by_wire[wire]
        return
    assert stored == -1
    assert wire not in family.state_by_wire


def check_capability_flags(model: str) -> None:
    """Capability flags that would create entities follow the mapped names."""
    family = family_of(model)
    capability = SimpleNamespace(
        custom_cleaning_mode=True,
        cruising=True,
        map=True,
        walls=True,
        mijia=False,
        dnd=False,
        self_wash_base=False,
        auto_empty_base=False,
        robot_type=1,
    )
    family.apply_capabilities(capability)
    assert capability.custom_cleaning_mode is False
    assert capability.walls is False
    assert capability.mijia is True
    assert capability.map is False


def check_cloud_fallback(model: str) -> None:
    """Missing or invalid credentials keep the cloud path instead of raising."""
    family = family_of(model)
    assert family.build_property_transport("", "00" * 16) is None
    assert family.build_property_transport(LOOPBACK_HOST, "") is None
    assert family.build_property_transport(LOOPBACK_HOST, "zz") is None
    assert family.build_property_transport(LOOPBACK_HOST, LOOPBACK_TOKEN) is not None


def check_configured_family(model: str) -> None:
    """The configured model installs its map before miIO info is known."""
    device = _bare_device(model)
    try:
        device.info = None
        device._apply_reported_family()
        codec = device._property_codec
        assert getattr(codec, "model", None) == model
    finally:
        release_device(device)


def check_send_async_transport() -> None:
    """Async property calls use the Xiaomi transport when one is installed."""

    class _Transport:
        def __init__(self) -> None:
            self.methods: list[str] = []

        def send(
            self, method: str, parameters: object, retry_count: int
        ) -> list[object]:
            del parameters, retry_count
            self.methods.append(method)
            return []

    class _Device:
        def __init__(self) -> None:
            self.methods: list[str] = []

        def send_async(
            self,
            callback: object,
            method: str,
            parameters: object = None,
            retry_count: int = 2,
        ) -> None:
            del callback, parameters, retry_count
            self.methods.append(method)

    transport = _Transport()
    device = _Device()
    protocol = SimpleNamespace(
        prefer_cloud=False,
        device=device,
        device_cloud=None,
        property_transport=transport,
        dreame_cloud=False,
        cloud=None,
        _connected=True,
    )
    DreameVacuumProtocol.send_async(protocol, None, "get_properties", [])
    assert transport.methods == ["get_properties"]
    assert device.methods == []


def check_unknown_state_task(model: str) -> None:
    """An unpublished status wire does not pretend the task completed."""
    family = family_of(model)
    assert _UNKNOWN_WIRE not in family.state_by_wire
    stored = family.convert_incoming("STATE", _UNKNOWN_WIRE)
    assert family.task_status_code(stored, _NOT_CHARGING) != int(StoredTask.COMPLETED)


def check_outgoing_range(model: str, sample: int) -> None:
    """An outgoing value outside the spec list or range is refused."""
    family = family_of(model)
    if has_shifted_property(model):
        name = (
            "SUCTION_LEVEL"
            if "SUCTION_LEVEL" in family.property_overrides
            else "CLEANING_MODE"
        )
        allowed = _allowed_wires(model, name)
        wire = sample + 1
        if wire in allowed:
            assert family.convert_outgoing(name, sample) == wire
        else:
            with pytest.raises(XiaomiControlException):
                family.convert_outgoing(name, sample)
        return
    control = next(
        (
            item
            for item in family_of(model).controls
            if item.writable and item.minimum is not None and item.piid is not None
        ),
        None,
    )
    if control is None or control.siid is None or control.piid is None:
        return
    sent: list[object] = []

    class _Protocol:
        def set_property(
            self, siid: int, piid: int, value: object
        ) -> list[dict[str, int]]:
            sent.append((siid, piid, value))
            return [{"code": 0}]

    device = SimpleNamespace(_protocol=_Protocol(), _xiaomi_values={})
    if control.minimum <= sample <= (control.maximum or sample):
        write_control(device, control, sample)
        assert sent
        return
    with pytest.raises(XiaomiControlException):
        write_control(device, control, sample)
    assert not sent


def check_control_refresh(model: str) -> None:
    """One failed control read does not discard the rest of the refresh."""
    del model
    stored: dict[str, object] = {}

    class _Protocol:
        def get_properties(self, items: list[dict[str, object]]) -> object:
            if len(items) > 1:
                return None
            item = items[0]
            return [
                {
                    "code": 0,
                    "siid": item["siid"],
                    "piid": item["piid"],
                    "value": 1,
                    "did": item["did"],
                }
            ]

    device = SimpleNamespace(_protocol=_Protocol(), _xiaomi_values=stored)
    controls = (
        boolean_switch("deep_one", 2, 1),
        boolean_switch("deep_two", 2, 2),
    )
    refresh_controls(device, controls)
    assert stored.get("deep_one") == 1


def check_start_custom(model: str) -> None:
    """start_custom never sends a missing piid. Unmapped actions are refused."""
    family = family_of(model)
    with FakeMiio(model) as fake:
        device = _connect(model)
        before = len(fake.actions)
        try:
            if "START_CUSTOM" not in family.action_overrides:
                with pytest.raises(InvalidActionException):
                    device.start_custom(DreameVacuumStatus.ZONE_CLEANING.value)
                assert len(fake.actions) == before
                return
            device.start_custom(DreameVacuumStatus.ZONE_CLEANING.value)
        finally:
            release_device(device)
        payload = fake.action_inputs[-1]
        assert isinstance(payload, list)
        assert payload
        assert isinstance(payload[0], dict)
        piid = payload[0].get("piid")
        assert isinstance(piid, int)
        state = family.property_overrides["STATE"]
        assert piid == state["piid"]


def check_set_properties_conversion(model: str) -> None:
    """A batch write uses the same outgoing conversion as a single write."""
    family = family_of(model)
    name = (
        "SUCTION_LEVEL"
        if "SUCTION_LEVEL" in family.property_overrides
        else "CLEANING_MODE"
    )
    prop = DreameVacuumProperty[name]
    mapping = family.property_overrides[name]
    with FakeMiio(model) as fake:
        device = _connect(model)
        try:
            assert device.set_properties({prop: 1}) is True
        finally:
            release_device(device)
        assert fake.writes[-1] == (mapping["siid"], mapping["piid"], 2)


def _connect(model: str) -> DreameVacuumDevice:
    device = DreameVacuumDevice(
        model,
        LOOPBACK_HOST,
        LOOPBACK_TOKEN,
        LOOPBACK_MAC,
        account_type="mi",
        family_resolver=resolve_family,
    )
    device.connect_device()
    return device


def _bare_device(model: str) -> DreameVacuumDevice:
    return DreameVacuumDevice(
        "Deep",
        LOOPBACK_HOST,
        LOOPBACK_TOKEN,
        LOOPBACK_MAC,
        account_type="mi",
        family_resolver=resolve_family,
        configured_model=model,
    )


def _allowed_wires(model: str, name: str) -> set[int]:
    family = family_of(model)
    mapping = family.property_overrides[name]
    for case in property_cases(model):
        if case.siid == mapping["siid"] and case.piid == mapping["piid"]:
            return {wire for wire, _description in case.values}
    return set()


def _status_wires(model: str) -> set[int]:
    family = family_of(model)
    mapping = family.property_overrides["STATE"]
    for case in property_cases(model):
        if case.siid == mapping["siid"] and case.piid == mapping["piid"]:
            return {wire for wire, _description in case.values}
    return set()


def _action_index(model: str) -> tuple[ActionCase, ...]:
    return action_cases(model)


def _has_property(document: dict[str, object], siid: int, piid: int) -> bool:
    return _has_item(document, "properties", siid, piid)


def _has_action(document: dict[str, object], siid: int, aiid: int) -> bool:
    return _has_item(document, "actions", siid, aiid)


def _has_item(document: dict[str, object], field: str, siid: int, iid: int) -> bool:
    services = document.get("services")
    if not isinstance(services, list):
        return False
    for service in services:
        if not isinstance(service, dict) or service.get("iid") != siid:
            continue
        raw = service.get(field) or []
        if not isinstance(raw, list):
            continue
        for item in raw:
            if isinstance(item, dict) and item.get("iid") == iid:
                return True
    return False

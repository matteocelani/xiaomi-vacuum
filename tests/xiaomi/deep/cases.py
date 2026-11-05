"""Spec-derived cases for one Xiaomi model. No assertions."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Final

from custom_components.dreame_vacuum.xiaomi.controls import XiaomiControl
from custom_components.dreame_vacuum.xiaomi.mapping import resolve_family
from custom_components.dreame_vacuum.xiaomi.model import XiaomiModel
from custom_components.dreame_vacuum.xiaomi.schedule import schedule_property_name
from tests.xiaomi.deep.corpus import SpecRecord, load_record, spec_token

_STRINGS: Final = Path("custom_components/dreame_vacuum/strings.json")
_ONE_INDEX: Final = frozenset({"CLEANING_MODE", "SUCTION_LEVEL"})
_REQUIRED_TOKENS: Final = frozenset(
    {"status", "fault", "battery-level", "charging-state"}
)
_MAP_NEEDLES: Final = (
    "map",
    "room",
    "zone",
    "wall",
    "furniture",
    "trajectory",
    "restricted",
    "segment",
    "sill",
    "carpet-display",
    "carpet-show",
    "carpet-obj",
    "history-map",
    "partition",
    "virtual",
    "points",
)
_COUNCIL_NEEDLES: Final = (
    "order",
    "schedule",
    "voice",
    "language",
    "ota",
    "remote",
    "user-defined",
    "user-sweep",
    "plugin",
    "self-check",
    "dnd-time",
    "enable-time",
    "direction",
    "spec-test",
)
_UNNAMED_TOKENS: Final = frozenset({"spec-test", "cmd", "flag"})
_PLAN: Final = "docs/unmapped-props-plan.md"
_DOCUMENTED_OMISSIONS: Final = {
    ("xiaomi.vacuum.b112", 10, 1): (
        "needs council: remember-state publishes only Close, so a switch cannot turn on. "
        f"See {_PLAN}."
    ),
    ("xiaomi.vacuum.b112bk", 10, 1): (
        "needs council: remember-state publishes only Close, so a switch cannot turn on. "
        f"See {_PLAN}."
    ),
    ("xiaomi.vacuum.b112gl", 10, 1): (
        "needs council: remember-state publishes only Close, so a switch cannot turn on. "
        f"See {_PLAN}."
    ),
    ("xiaomi.vacuum.d109gl", 20, 7): (
        "needs council: sewage-self-cleaning has no description and no known station meaning. "
        f"See {_PLAN}."
    ),
    ("xiaomi.vacuum.d109gl", 20, 8): (
        "needs council: self-cleaning-time is an unnamed uint32 with no unit. "
        f"See {_PLAN}."
    ),
}


@dataclass(frozen=True, slots=True)
class PropertyCase:
    """One spec property plus how this model treats it."""

    model: str
    siid: int
    piid: int
    token: str
    description: str
    format: str
    access: tuple[str, ...]
    unit: str | None
    values: tuple[tuple[int, str], ...]
    value_range: tuple[int, int, int] | None
    mapped_name: str | None
    omission: str | None

    @property
    def case_id(self) -> str:
        """Pytest id for this property."""
        return f"p{self.siid}-{self.piid}"


@dataclass(frozen=True, slots=True)
class ActionCase:
    """One spec action plus how this model treats it."""

    model: str
    siid: int
    aiid: int
    token: str
    description: str
    inputs: tuple[int, ...]
    mapped_name: str | None
    omission: str | None

    @property
    def case_id(self) -> str:
        """Pytest id for this action."""
        return f"a{self.siid}-{self.aiid}"


@dataclass(frozen=True, slots=True)
class ValueCase:
    """One spec value-list entry on a mapped property."""

    model: str
    name: str
    wire: int
    description: str

    @property
    def case_id(self) -> str:
        """Pytest id for this wire value."""
        return f"{self.name}-{self.wire}"


@dataclass(frozen=True, slots=True)
class FaultCase:
    """One spec fault code, or a note that the spec publishes none."""

    model: str
    code: int | None
    description: str

    @property
    def case_id(self) -> str:
        """Pytest id for this fault."""
        if self.code is None:
            return "no-value-list"
        return f"fault-{self.code}"


@dataclass(frozen=True, slots=True)
class ControlCase:
    """One declarative control checked against its spec item."""

    model: str
    key: str
    domain: str
    siid: int | None
    piid: int | None
    aiid: int | None
    writable: bool
    options: tuple[tuple[int, str], ...]
    minimum: int | None
    maximum: int | None
    step: int
    value_kind: str

    @property
    def case_id(self) -> str:
        """Pytest id for this control."""
        return self.key


@dataclass(frozen=True, slots=True)
class AddressCase:
    """A mapped property or action address that must exist in the spec."""

    model: str
    kind: str
    name: str
    siid: int
    iid: int

    @property
    def case_id(self) -> str:
        """Pytest id for this address."""
        return f"{self.kind}-{self.name}"


def family_of(model: str) -> XiaomiModel:
    """Return the installed record for a model id."""
    family = resolve_family(model)
    if family is None:
        raise KeyError(model)
    return family


def record_of(model: str) -> SpecRecord:
    """Return the fetched spec record for a model id."""
    return load_record(model)


def property_cases(model: str) -> tuple[PropertyCase, ...]:
    """Build one case per spec property."""
    family = family_of(model)
    record = record_of(model)
    mapped = _property_names(family)
    found: list[PropertyCase] = []
    for siid, item in _properties(record.document):
        piid = _int_field(item, "iid")
        description = _text(item.get("description"))
        token = spec_token(_text(item.get("type")))
        access = _strings(item.get("access"))
        values = _value_list(item.get("value-list"))
        bounds = _value_range(item.get("value-range"))
        unit = item.get("unit")
        name = mapped.get((siid, piid)) or schedule_property_name(model, siid, piid)
        omission = (
            None
            if name
            else _property_omission(
                model,
                siid,
                piid,
                token,
                description,
                access,
                _text(item.get("format")),
            )
        )
        found.append(
            PropertyCase(
                model=model,
                siid=siid,
                piid=piid,
                token=token,
                description=description,
                format=_text(item.get("format")),
                access=access,
                unit=unit if isinstance(unit, str) else None,
                values=values,
                value_range=bounds,
                mapped_name=name,
                omission=omission,
            )
        )
    return tuple(found)


def action_cases(model: str) -> tuple[ActionCase, ...]:
    """Build one case per spec action."""
    family = family_of(model)
    record = record_of(model)
    mapped = _action_names(family)
    found: list[ActionCase] = []
    for siid, item in _actions(record.document):
        aiid = _int_field(item, "iid")
        description = _text(item.get("description"))
        token = spec_token(_text(item.get("type")))
        inputs = _int_list(item.get("in"))
        name = mapped.get((siid, aiid))
        omission = None if name else _action_omission(siid, token, description, inputs)
        found.append(
            ActionCase(
                model=model,
                siid=siid,
                aiid=aiid,
                token=token,
                description=description,
                inputs=inputs,
                mapped_name=name,
                omission=omission,
            )
        )
    return tuple(found)


def value_cases(model: str) -> tuple[ValueCase, ...]:
    """Build one case per value-list entry of a codec property."""
    family = family_of(model)
    by_address = {(case.siid, case.piid): case for case in property_cases(model)}
    found: list[ValueCase] = []
    for name in (
        "STATE",
        "TASK_STATUS",
        "CLEANING_MODE",
        "SUCTION_LEVEL",
        "CHARGING_STATUS",
    ):
        mapping = family.property_overrides.get(name)
        if mapping is None:
            continue
        case = by_address.get((mapping["siid"], mapping["piid"]))
        if case is None:
            continue
        for wire, description in case.values:
            found.append(
                ValueCase(model=model, name=name, wire=wire, description=description)
            )
    return tuple(found)


def fault_cases(model: str) -> tuple[FaultCase, ...]:
    """Build one case per spec fault code, or a single empty case."""
    family = family_of(model)
    mapping = family.property_overrides.get("ERROR")
    if mapping is None:
        return (FaultCase(model, None, ""),)
    case = next(
        (
            item
            for item in property_cases(model)
            if item.siid == mapping["siid"] and item.piid == mapping["piid"]
        ),
        None,
    )
    if case is None or not case.values:
        return (FaultCase(model, None, ""),)
    return tuple(
        FaultCase(model, wire, description) for wire, description in case.values
    )


def control_cases(model: str) -> tuple[ControlCase, ...]:
    """Build one case per declarative control."""
    family = family_of(model)
    return tuple(_control_case(model, control) for control in family.controls)


def address_cases(model: str) -> tuple[AddressCase, ...]:
    """Build one case per mapped property and action address."""
    family = family_of(model)
    found: list[AddressCase] = []
    for name, mapping in family.property_overrides.items():
        found.append(
            AddressCase(model, "property", name, mapping["siid"], mapping["piid"])
        )
    for name, mapping in family.action_overrides.items():
        found.append(
            AddressCase(model, "action", name, mapping["siid"], mapping["aiid"])
        )
    for control in family.controls:
        if control.siid is None:
            continue
        if control.piid is not None:
            found.append(
                AddressCase(model, "control", control.key, control.siid, control.piid)
            )
        if control.aiid is not None:
            found.append(
                AddressCase(
                    model, "control-action", control.key, control.siid, control.aiid
                )
            )
    return tuple(found)


def has_start_custom(model: str) -> bool:
    """Return whether the record maps the custom-clean action."""
    return "START_CUSTOM" in family_of(model).action_overrides


def has_shifted_property(model: str) -> bool:
    """Return whether outgoing cleaning mode or suction uses the shared offset."""
    names = family_of(model).property_overrides
    return "CLEANING_MODE" in names or "SUCTION_LEVEL" in names


def has_controls(model: str) -> bool:
    """Return whether the record declares direct controls."""
    return bool(family_of(model).controls)


def error_translations() -> dict[str, str]:
    """Return English error-sensor state labels."""
    loaded = json.loads(_STRINGS.read_text(encoding="utf-8"))
    entity = loaded["entity"]
    if not isinstance(entity, dict):
        return {}
    sensor = entity["sensor"]
    if not isinstance(sensor, dict):
        return {}
    error = sensor["error"]
    if not isinstance(error, dict):
        return {}
    states = error["state"]
    if not isinstance(states, dict):
        return {}
    return {key: value for key, value in states.items() if isinstance(value, str)}


def entity_translations() -> dict[str, dict[str, object]]:
    """Return the English entity catalog."""
    loaded = json.loads(_STRINGS.read_text(encoding="utf-8"))
    entity = loaded["entity"]
    if not isinstance(entity, dict):
        return {}
    return {key: value for key, value in entity.items() if isinstance(value, dict)}


def _control_case(model: str, control: XiaomiControl) -> ControlCase:
    return ControlCase(
        model=model,
        key=control.key,
        domain=str(control.domain),
        siid=control.siid,
        piid=control.piid,
        aiid=control.aiid,
        writable=control.writable,
        options=control.options,
        minimum=control.minimum,
        maximum=control.maximum,
        step=control.step,
        value_kind=str(control.value_kind),
    )


def _property_names(family: XiaomiModel) -> dict[tuple[int, int], str]:
    found: dict[tuple[int, int], str] = {}
    for name, mapping in family.property_overrides.items():
        found[(mapping["siid"], mapping["piid"])] = name
    for control in family.controls:
        if control.siid is None or control.piid is None:
            continue
        found.setdefault((control.siid, control.piid), control.key)
    return found


def _action_names(family: XiaomiModel) -> dict[tuple[int, int], str]:
    found: dict[tuple[int, int], str] = {}
    for name, mapping in family.action_overrides.items():
        found[(mapping["siid"], mapping["aiid"])] = name
    for control in family.controls:
        if control.siid is None or control.aiid is None:
            continue
        found.setdefault((control.siid, control.aiid), control.key)
    return found


def _properties(
    document: Mapping[str, object],
) -> list[tuple[int, Mapping[str, object]]]:
    return _items(document, "properties")


def _actions(document: Mapping[str, object]) -> list[tuple[int, Mapping[str, object]]]:
    return _items(document, "actions")


def _items(
    document: Mapping[str, object], field: str
) -> list[tuple[int, Mapping[str, object]]]:
    services = document.get("services")
    if not isinstance(services, list):
        return []
    found: list[tuple[int, Mapping[str, object]]] = []
    for service in services:
        if not isinstance(service, dict):
            continue
        siid = service.get("iid")
        if not isinstance(siid, int):
            continue
        raw = service.get(field) or []
        if not isinstance(raw, list):
            continue
        for item in raw:
            if isinstance(item, dict):
                found.append((siid, item))
    return found


def _property_omission(
    model: str,
    siid: int,
    piid: int,
    token: str,
    description: str,
    access: tuple[str, ...],
    value_format: str,
) -> str | None:
    documented = _DOCUMENTED_OMISSIONS.get((model, siid, piid))
    if documented:
        return documented
    if token in _REQUIRED_TOKENS:
        return None
    if siid == 1:
        return "identity: manufacturer, model, and firmware come from miIO.info."
    if not access:
        return "no ha meaning: the spec publishes no read, write, or notify access."
    blob = f"{token} {description}".lower()
    if any(needle in blob for needle in _MAP_NEEDLES):
        return "map: map geometry stays unmapped until map support."
    if any(needle in blob for needle in _COUNCIL_NEEDLES):
        return "needs council: the spec item is not a parameter-free vacuum control."
    if token in _UNNAMED_TOKENS:
        return "no ha meaning: the spec item has no published name."
    if value_format == "string":
        return "no ha meaning: the value is an opaque string."
    if "write" not in access:
        return "no ha meaning: read-only telemetry is not a mapped entity."
    return None


def _action_omission(
    siid: int, token: str, description: str, inputs: tuple[int, ...]
) -> str:
    if siid == 1:
        return "identity: device-information actions are not user controls."
    blob = f"{token} {description}".lower()
    if any(needle in blob for needle in _MAP_NEEDLES):
        return "map: the action edits map geometry."
    if inputs:
        return "needs council: the action takes parameters and is not a button."
    if any(needle in blob for needle in _COUNCIL_NEEDLES):
        return "needs council: the action is not a parameter-free vacuum command."
    return "needs council: the action is not a vacuum, charge, or pause command."


def _value_list(raw: object) -> tuple[tuple[int, str], ...]:
    if not isinstance(raw, list):
        return ()
    found: list[tuple[int, str]] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        value = item.get("value")
        if isinstance(value, int) and not isinstance(value, bool):
            found.append((value, _text(item.get("description"))))
    return tuple(found)


def _value_range(raw: object) -> tuple[int, int, int] | None:
    if not isinstance(raw, list) or len(raw) != 3:
        return None
    start, end, step = raw
    if all(
        isinstance(item, int) and not isinstance(item, bool)
        for item in (start, end, step)
    ):
        return (start, end, step)
    return None


def _strings(raw: object) -> tuple[str, ...]:
    if not isinstance(raw, list):
        return ()
    return tuple(item for item in raw if isinstance(item, str))


def _int_list(raw: object) -> tuple[int, ...]:
    if not isinstance(raw, list):
        return ()
    return tuple(
        item for item in raw if isinstance(item, int) and not isinstance(item, bool)
    )


def _int_field(item: Mapping[str, object], key: str) -> int:
    value = item.get(key)
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    raise TypeError(key)


def _text(value: object) -> str:
    if isinstance(value, str):
        return value
    return ""


def shifted_names() -> frozenset[str]:
    """Return property names whose outgoing codec adds one."""
    return _ONE_INDEX

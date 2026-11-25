"""MIoT spec robot: properties, actions, faults, and a floor plan."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import threading
from typing import Final

from custom_components.xiaomi_robot_vacuum.xiaomi.model import StoredState, XiaomiModel
from tests.virtual.floor_plan import encode_floor_plan, room_summary
from tests.xiaomi.deep.corpus import spec_token

_CHARGING_WORDS: Final = ("charg", "dock")
_IDLE_WORD: Final = "idle"
_ERROR_WORDS: Final = ("error", "fault")
_LIFE_LEVEL: Final = 80
_BATTERY_LEVEL: Final = 80
_CHARGING_FLAG: Final = 1
_NOT_CHARGING_FLAG: Final = 2
_NO_FAULT: Final = 0
_REJECTED: Final = -1000
_MAP_WORDS: Final = (
    "map",
    "room",
    "segment",
    "zone",
    "point",
    "wall",
    "carpet",
    "furniture",
    "path",
)
_START_WORDS: Final = (
    "start-sweep",
    "start-clean",
    "start-mop",
    "start-only",
    "start-room-sweep",
    "start-vacuum-room-sweep",
)
_PAUSE_WORDS: Final = ("pause",)
_CHARGE_WORDS: Final = ("start-charge", "start-charging")
_STOP_WORDS: Final = ("stop-sweep", "stop-clean", "stop-charging")


@dataclass(frozen=True, slots=True)
class SpecProperty:
    """One property published by a MIoT spec."""

    siid: int
    piid: int
    token: str
    value_format: str
    access: frozenset[str]
    values: tuple[int, ...] | None
    descriptions: tuple[tuple[int, str], ...]
    minimum: int | None
    maximum: int | None
    step: int | None

    def allows(self, value: object) -> bool:
        """Return whether the value matches this property's format and limits."""
        if self.value_format == "bool":
            return isinstance(value, bool) or (
                isinstance(value, int)
                and not isinstance(value, bool)
                and value in (0, 1)
            )
        if self.value_format == "string":
            return isinstance(value, str)
        if self.value_format == "float":
            return isinstance(value, (int, float)) and not isinstance(value, bool)
        if isinstance(value, bool) or not isinstance(value, int):
            return False
        if self.values is not None:
            return value in self.values
        if self.minimum is not None and value < self.minimum:
            return False
        if self.maximum is not None and value > self.maximum:
            return False
        return not (
            self.step is not None
            and self.step > 0
            and self.minimum is not None
            and (value - self.minimum) % self.step != 0
        )


@dataclass(frozen=True, slots=True)
class SpecAction:
    """One action published by a MIoT spec."""

    siid: int
    aiid: int
    token: str
    inputs: tuple[int, ...]


def load_properties(
    document: Mapping[str, object],
) -> dict[tuple[int, int], SpecProperty]:
    """Index every property in a MIoT instance document."""
    properties: dict[tuple[int, int], SpecProperty] = {}
    for service in _services(document):
        siid = service.get("iid")
        if not isinstance(siid, int):
            continue
        raw_properties = service.get("properties")
        if not isinstance(raw_properties, list):
            continue
        for item in raw_properties:
            prop = _property(siid, item)
            if prop is not None:
                properties[(prop.siid, prop.piid)] = prop
    return properties


def load_actions(document: Mapping[str, object]) -> dict[tuple[int, int], SpecAction]:
    """Index every action in a MIoT instance document."""
    actions: dict[tuple[int, int], SpecAction] = {}
    for service in _services(document):
        siid = service.get("iid")
        if not isinstance(siid, int):
            continue
        raw_actions = service.get("actions")
        if not isinstance(raw_actions, list):
            continue
        for item in raw_actions:
            action = _action(siid, item)
            if action is not None:
                actions[(action.siid, action.aiid)] = action
    return actions


class SpecRobot:
    """In-memory robot whose values and actions come from one spec document."""

    def __init__(
        self,
        model: str,
        document: Mapping[str, object],
        *,
        mac: str = "00:00:00:00:00:00",
        strict: bool = False,
    ) -> None:
        self.model = model
        self.mac = mac
        self.strict = strict
        self.properties = load_properties(document)
        self.actions_by_address = load_actions(document)
        self.floor_plan = encode_floor_plan()
        self.writes: list[tuple[int, int, object]] = []
        self.actions: list[tuple[int, int]] = []
        self.action_inputs: list[object] = []
        self._family: XiaomiModel | None = None
        self._values: dict[tuple[int, int], object] = {}
        self._lock = threading.Lock()
        for prop in self.properties.values():
            self._values[(prop.siid, prop.piid)] = _initial_value(prop, model)
        self._publish_map_text()

    def apply_family(self, family: XiaomiModel) -> None:
        """Seed mapped addresses with wires this family's codec accepts."""
        with self._lock:
            self._family = family
            self._apply_family_locked(family)

    def dispatch(self, method: object, params: object) -> object | None:
        """Answer one miIO or cloud call. None means the method is unknown."""
        if method == "miIO.info":
            return {
                "model": self.model,
                "fw_ver": "1.0_1",
                "mac": self.mac,
                "hw_ver": "Linux",
                "netif": {"localIp": "127.0.0.1"},
            }
        if method == "get_properties" and isinstance(params, list):
            return [self.read(item) for item in params if isinstance(item, dict)]
        if method == "set_properties" and isinstance(params, list):
            return [self.write(item) for item in params if isinstance(item, dict)]
        if method == "action" and isinstance(params, dict):
            return self.invoke(params)
        return None

    def read(self, item: Mapping[str, object]) -> dict[str, object]:
        """Return one property result, including a spec rejection."""
        siid = item.get("siid")
        piid = item.get("piid")
        if not isinstance(siid, int) or not isinstance(piid, int):
            return {"code": _REJECTED, "siid": siid, "piid": piid}
        with self._lock:
            if (siid, piid) not in self._values:
                return {
                    "did": item.get("did", ""),
                    "siid": siid,
                    "piid": piid,
                    "code": _REJECTED,
                }
            value = self._values[(siid, piid)]
        return {
            "did": item.get("did", ""),
            "siid": siid,
            "piid": piid,
            "code": 0,
            "value": value,
        }

    def write(self, item: Mapping[str, object]) -> dict[str, object]:
        """Store a legal write. An illegal value is refused and left unchanged."""
        siid = item.get("siid")
        piid = item.get("piid")
        if not isinstance(siid, int) or not isinstance(piid, int):
            return {"code": _REJECTED, "siid": siid, "piid": piid}
        value = item.get("value")
        with self._lock:
            allowed = self._allows_locked(siid, piid, value)
            if not allowed:
                return {
                    "did": item.get("did", ""),
                    "siid": siid,
                    "piid": piid,
                    "code": _REJECTED,
                }
            self._values[(siid, piid)] = value
            self.writes.append((siid, piid, value))
        return {"did": item.get("did", ""), "siid": siid, "piid": piid, "code": 0}

    def invoke(self, params: Mapping[str, object]) -> dict[str, object]:
        """Run one action and move the published status when the spec names it."""
        siid = params.get("siid")
        aiid = params.get("aiid")
        if not isinstance(siid, int) or not isinstance(aiid, int):
            return {"code": -1}
        incoming = params.get("in")
        with self._lock:
            action = self.actions_by_address.get((siid, aiid))
            if action is None and self.strict:
                return {"code": -1}
            if action is not None and not _inputs_present(action, incoming):
                return {"code": -1}
            self.actions.append((siid, aiid))
            self.action_inputs.append(incoming)
            self._apply_action_locked(siid, aiid, action)
        return {"code": 0, "out": []}

    def set_stored(self, stored: StoredState) -> None:
        """Publish the lowest wire that this family stores as stored."""
        with self._lock:
            self._set_stored_locked(stored)

    def set_fault(self) -> int | None:
        """Publish a non-zero fault and the error status wire."""
        with self._lock:
            code = self._fault_code_locked()
            if code is None:
                return None
            for prop in self.properties.values():
                if prop.token == "fault":
                    self._values[(prop.siid, prop.piid)] = code
            self._set_stored_locked(StoredState.ERROR)
            return code

    def value(self, siid: int, piid: int) -> object:
        """Return the current stored value for one address."""
        with self._lock:
            return self._values.get((siid, piid))

    def _apply_family_locked(self, family: XiaomiModel) -> None:
        for name, mapping in family.property_overrides.items():
            siid = mapping.get("siid")
            piid = mapping.get("piid")
            if not isinstance(siid, int) or not isinstance(piid, int):
                continue
            if self.strict and (siid, piid) not in self.properties:
                continue
            chosen = _family_seed(name, family)
            if chosen is None:
                continue
            if not self._allows_locked(siid, piid, chosen):
                continue
            self._values[(siid, piid)] = chosen
        self._set_stored_locked(StoredState.CHARGING)

    def _set_stored_locked(self, stored: StoredState) -> None:
        family = self._family
        if family is None:
            self._set_status_description_locked(stored)
            return
        wires = [
            wire for wire, value in family.state_by_wire.items() if value == int(stored)
        ]
        mapping = family.property_overrides.get("STATE")
        if not wires or mapping is None:
            self._set_status_description_locked(stored)
            return
        siid = mapping["siid"]
        piid = mapping["piid"]
        wire = min(wires)
        if self._allows_locked(siid, piid, wire):
            self._values[(siid, piid)] = wire
        charging = stored == StoredState.CHARGING
        self._set_charging_flag_locked(charging)

    def _set_status_description_locked(self, stored: StoredState) -> None:
        for prop in self.properties.values():
            if prop.token != "status":
                continue
            chosen = _described_status(prop, stored)
            if chosen is not None:
                self._values[(prop.siid, prop.piid)] = chosen

    def _set_charging_flag_locked(self, charging: bool) -> None:
        family = self._family
        if family is not None:
            mapping = family.property_overrides.get("CHARGING_STATUS")
            if mapping is not None:
                flag = _CHARGING_FLAG if charging else _NOT_CHARGING_FLAG
                siid = mapping["siid"]
                piid = mapping["piid"]
                if self._allows_locked(siid, piid, flag):
                    self._values[(siid, piid)] = flag
        for prop in self.properties.values():
            if prop.token != "charging-state":
                continue
            flag = _flag_for(prop, charging)
            if flag is not None:
                self._values[(prop.siid, prop.piid)] = flag

    def _apply_action_locked(
        self, siid: int, aiid: int, action: SpecAction | None
    ) -> None:
        family = self._family
        if family is not None:
            names = {
                name: (item["siid"], item["aiid"])
                for name, item in family.action_overrides.items()
                if "siid" in item and "aiid" in item
            }
            address = (siid, aiid)
            if address in (names.get("START"), names.get("RESUME")):
                self._set_stored_locked(StoredState.SWEEPING)
                return
            if address == names.get("PAUSE"):
                self._set_stored_locked(StoredState.PAUSED)
                return
            if address == names.get("CHARGE"):
                self._set_stored_locked(StoredState.CHARGING)
                return
            if address == names.get("STOP"):
                self._set_stored_locked(StoredState.IDLE)
                return
        if action is None:
            return
        token = action.token
        if token.startswith("reset-") and token.endswith("-life"):
            self._reset_life_locked(token)
            return
        if _starts_with(token, _START_WORDS):
            if "mop" in token and "sweep" not in token:
                self._set_stored_locked(StoredState.MOPPING)
            else:
                self._set_stored_locked(StoredState.SWEEPING)
            return
        if _starts_with(token, _PAUSE_WORDS):
            self._set_stored_locked(StoredState.PAUSED)
            return
        if _starts_with(token, _CHARGE_WORDS):
            self._set_stored_locked(StoredState.CHARGING)
            return
        if _starts_with(token, _STOP_WORDS):
            self._set_stored_locked(StoredState.IDLE)

    def _reset_life_locked(self, token: str) -> None:
        needle = token.removeprefix("reset-").removesuffix("-life")
        for prop in self.properties.values():
            if needle not in prop.token or "life" not in prop.token:
                continue
            filled = _top_of(prop)
            if filled is not None and prop.allows(filled):
                self._values[(prop.siid, prop.piid)] = filled

    def _fault_code_locked(self) -> int | None:
        for prop in self.properties.values():
            if prop.token != "fault":
                continue
            if prop.values:
                nonzero = [item for item in prop.values if item != _NO_FAULT]
                if nonzero:
                    return min(nonzero)
            if (
                prop.minimum is not None
                and prop.maximum is not None
                and prop.minimum <= 1 <= prop.maximum
            ):
                return 1
        return None

    def _allows_locked(self, siid: int, piid: int, value: object) -> bool:
        prop = self.properties.get((siid, piid))
        if prop is None:
            return not self.strict
        return prop.allows(value)

    def _publish_map_text(self) -> None:
        summary = room_summary()
        for prop in self.properties.values():
            if prop.value_format != "string":
                continue
            if not any(word in prop.token for word in _MAP_WORDS):
                continue
            if "map" in prop.token and "room" not in prop.token:
                self._values[(prop.siid, prop.piid)] = self.floor_plan
            else:
                self._values[(prop.siid, prop.piid)] = summary


def _services(document: Mapping[str, object]) -> list[Mapping[str, object]]:
    raw = document.get("services")
    if not isinstance(raw, list):
        return []
    return [item for item in raw if isinstance(item, Mapping)]


def _property(siid: int, item: object) -> SpecProperty | None:
    if not isinstance(item, Mapping):
        return None
    piid = item.get("iid")
    type_urn = item.get("type")
    value_format = item.get("format")
    if not isinstance(piid, int) or not isinstance(type_urn, str):
        return None
    if not isinstance(value_format, str):
        return None
    access = item.get("access")
    names = access if isinstance(access, list) else []
    values, descriptions = _value_list(item.get("value-list"))
    minimum, maximum, step = _value_range(item.get("value-range"))
    return SpecProperty(
        siid=siid,
        piid=piid,
        token=spec_token(type_urn),
        value_format=_normalize_format(value_format),
        access=frozenset(name for name in names if isinstance(name, str)),
        values=values,
        descriptions=descriptions,
        minimum=minimum,
        maximum=maximum,
        step=step,
    )


def _action(siid: int, item: object) -> SpecAction | None:
    if not isinstance(item, Mapping):
        return None
    aiid = item.get("iid")
    type_urn = item.get("type")
    if not isinstance(aiid, int) or not isinstance(type_urn, str):
        return None
    raw_inputs = item.get("in")
    inputs: list[int] = []
    if isinstance(raw_inputs, list):
        inputs.extend(value for value in raw_inputs if isinstance(value, int))
    return SpecAction(
        siid=siid,
        aiid=aiid,
        token=spec_token(type_urn),
        inputs=tuple(inputs),
    )


def _value_list(
    raw: object,
) -> tuple[tuple[int, ...] | None, tuple[tuple[int, str], ...]]:
    if not isinstance(raw, list):
        return None, ()
    values: list[int] = []
    descriptions: list[tuple[int, str]] = []
    for item in raw:
        if not isinstance(item, Mapping):
            continue
        value = item.get("value")
        if isinstance(value, bool) or not isinstance(value, int):
            continue
        description = item.get("description")
        text = description.lower() if isinstance(description, str) else ""
        values.append(value)
        descriptions.append((value, text))
    if not values:
        return None, ()
    return tuple(values), tuple(descriptions)


def _value_range(raw: object) -> tuple[int | None, int | None, int | None]:
    if not isinstance(raw, list) or len(raw) < 2:
        return None, None, None
    minimum = raw[0]
    maximum = raw[1]
    step = raw[2] if len(raw) > 2 else 1
    if isinstance(minimum, bool) or not isinstance(minimum, int):
        return None, None, None
    if isinstance(maximum, bool) or not isinstance(maximum, int):
        return None, None, None
    if isinstance(step, bool) or not isinstance(step, int) or step <= 0:
        step = 1
    return minimum, maximum, step


def _normalize_format(raw: str) -> str:
    if raw == "bool":
        return "bool"
    if raw == "string":
        return "string"
    if raw == "float":
        return "float"
    return "int"


def _initial_value(prop: SpecProperty, model: str) -> object:
    if prop.value_format == "bool":
        return False
    if prop.value_format == "string":
        if prop.token == "manufacturer":
            return "Xiaomi"
        if prop.token == "model":
            return model
        if prop.token == "firmware-revision":
            return "1.0_1"
        if prop.token == "serial-number":
            return "LAB000000"
        return ""
    if prop.value_format == "float":
        return 0
    if prop.token == "status":
        chosen = _described_status(prop, StoredState.CHARGING)
        if chosen is not None:
            return chosen
    if prop.token == "fault":
        if prop.values is not None and _NO_FAULT in prop.values:
            return _NO_FAULT
        if prop.minimum is not None and prop.minimum <= _NO_FAULT:
            return _NO_FAULT
    if prop.token in {"battery-level", "filter-life-level", "brush-life-level"} or (
        prop.token.endswith("life-level")
    ):
        return _clamp_int(
            prop, _LIFE_LEVEL if prop.token != "battery-level" else _BATTERY_LEVEL
        )
    if prop.token.endswith("left-time"):
        return _clamp_int(prop, 100)
    if prop.values:
        return prop.values[0]
    if prop.minimum is not None:
        return prop.minimum
    return 0


def _clamp_int(prop: SpecProperty, wanted: int) -> int:
    if prop.values:
        return wanted if wanted in prop.values else prop.values[0]
    if prop.minimum is not None and wanted < prop.minimum:
        return prop.minimum
    if prop.maximum is not None and wanted > prop.maximum:
        return prop.maximum
    return wanted


def _described_status(prop: SpecProperty, stored: StoredState) -> int | None:
    if not prop.descriptions:
        return None
    if stored == StoredState.CHARGING:
        return _match_description(prop, _CHARGING_WORDS) or _match_description(
            prop, (_IDLE_WORD,)
        )
    if stored == StoredState.SWEEPING:
        return _match_description(prop, ("sweep", "clean"))
    if stored == StoredState.MOPPING:
        return _match_description(prop, ("mop", "sweep"))
    if stored == StoredState.PAUSED:
        return _match_description(prop, ("paus",))
    if stored == StoredState.ERROR:
        return _match_description(prop, _ERROR_WORDS)
    if stored == StoredState.IDLE:
        return _match_description(prop, (_IDLE_WORD, "charg"))
    if stored == StoredState.RETURNING:
        return _match_description(prop, ("charg", "return"))
    return None


def _match_description(
    prop: SpecProperty, words: tuple[str, ...], *, skip: tuple[str, ...] = ()
) -> int | None:
    for value, text in prop.descriptions:
        if any(word in text for word in skip):
            continue
        if any(word in text for word in words):
            return value
    return None


def _family_seed(name: str, family: XiaomiModel) -> object | None:
    del family
    if name == "BATTERY_LEVEL":
        return _BATTERY_LEVEL
    if name == "ERROR":
        return _NO_FAULT
    if name.endswith(("_LEFT", "_LIFE")):
        return _LIFE_LEVEL
    return None


def _flag_for(prop: SpecProperty, charging: bool) -> int | None:
    if charging:
        matched = _match_description(prop, ("charging",), skip=("not",))
        if matched is not None:
            return matched
        if prop.allows(_CHARGING_FLAG):
            return _CHARGING_FLAG
        return None
    matched = _match_description(prop, ("not-charging", "not charging", "not"))
    if matched is not None:
        return matched
    if prop.allows(_NOT_CHARGING_FLAG):
        return _NOT_CHARGING_FLAG
    return None


def _inputs_present(action: SpecAction, incoming: object) -> bool:
    if not action.inputs:
        return True
    if not isinstance(incoming, list):
        return False
    present: set[int] = set()
    for item in incoming:
        if not isinstance(item, Mapping):
            return False
        piid = item.get("piid")
        if not isinstance(piid, int) or "value" not in item:
            return False
        present.add(piid)
    return set(action.inputs) <= present


def _starts_with(token: str, words: tuple[str, ...]) -> bool:
    return any(token == word or token.startswith(word) for word in words)


def _top_of(prop: SpecProperty) -> int | None:
    if prop.values:
        return max(prop.values)
    if prop.maximum is not None:
        return prop.maximum
    return None

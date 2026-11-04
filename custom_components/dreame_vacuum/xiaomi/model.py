"""Codec shared by every Xiaomi vacuum model."""

from __future__ import annotations

from collections.abc import Collection, Mapping
from dataclasses import dataclass, replace
from enum import IntEnum
from typing import Final, Protocol, runtime_checkable

from .controls import XiaomiControl, refresh_controls
from .exceptions import XiaomiTransportException
from .transport import MiioPropertyTransport

MODEL_S20_PLUS: Final = "xiaomi.vacuum.b108gl"
MODEL_X20: Final = "xiaomi.vacuum.c101eu"
MODEL_X20_MAX: Final = "xiaomi.vacuum.d109gl"
MODEL_X20_PRO: Final = "xiaomi.vacuum.d102gl"
MODEL_ROBOT_VACUUM_5: Final = "xiaomi.vacuum.ov31gl"
MODEL_ROBOT_VACUUM_5_PRO: Final = "xiaomi.vacuum.ov21gl"
MODEL_ROBOT_VACUUM_6: Final = "xiaomi.vacuum.pv32gl"
MODEL_ROBOT_VACUUM_6_MAX: Final = "xiaomi.vacuum.pv11gl"
MODEL_ROBOT_VACUUM_6_PRO: Final = "xiaomi.vacuum.pv21gl"
MODEL_S60_PLUS: Final = "xiaomi.vacuum.pv51gl"
MODEL_S60: Final = "xiaomi.vacuum.pv81gl"
MODEL_S40: Final = "xiaomi.vacuum.ov81gl"
MODEL_S40_PRO: Final = "xiaomi.vacuum.ov71gl"
MODEL_S40C: Final = "xiaomi.vacuum.e101gb"
MODEL_H40: Final = "xiaomi.vacuum.ov51gl"
MODEL_H50: Final = "xiaomi.vacuum.ov43gb"
MODEL_H50_PRO: Final = "xiaomi.vacuum.ov42gl"
MODEL_H50_PRO_ROLLER: Final = "xiaomi.vacuum.qv41gl"
MODEL_H50_ROLLER: Final = "xiaomi.vacuum.qv42gl"
MODEL_E10: Final = "xiaomi.vacuum.b112"
MODEL_E12: Final = "xiaomi.vacuum.b112gl"
MODEL_E10C: Final = "xiaomi.vacuum.b112bk"
MODEL_E5: Final = "xiaomi.vacuum.c108"
MODEL_S12: Final = "xiaomi.vacuum.b106eu"
MODEL_S20: Final = "xiaomi.vacuum.d106gl"
MODEL_T12: Final = "xiaomi.vacuum.b106bk"
MODEL_MIJIA_ROBOT_VACUUM_6: Final = "xiaomi.vacuum.pv32cn"
MODEL_MIJIA_7C: Final = "xiaomi.vacuum.qv41cn"
MODEL_MIJIA_M40_S: Final = "xiaomi.vacuum.ov31cn"
MODEL_MIJIA_5_PRO: Final = "xiaomi.vacuum.ov21cn"
MODEL_MIJIA_5C: Final = "xiaomi.vacuum.ov42cn"
MODEL_MIJIA_SWEEP_MOP_2: Final = "xiaomi.vacuum.c101"
MODEL_MIJIA_SWEEP_MOP_3: Final = "xiaomi.vacuum.c104"
MODEL_MIJIA_3C: Final = "xiaomi.vacuum.c103"
MODEL_MIJIA_M30: Final = "xiaomi.vacuum.d102ev"
MODEL_MIJIA_6_MAX: Final = "xiaomi.vacuum.pv11cn"
MODEL_MIJIA_6_PRO: Final = "xiaomi.vacuum.pv21cn"
MODEL_MIJIA_7_MAX: Final = "xiaomi.vacuum.qv12cn"
MODEL_MIJIA_H40: Final = "xiaomi.vacuum.d101"
MODEL_MIJIA_M30_PRO: Final = "xiaomi.vacuum.c107"
MODEL_MIJIA_ROBOT_VACUUM_4: Final = "xiaomi.vacuum.ov81cn"
MODEL_MIJIA_ROBOT_VACUUM_5: Final = "xiaomi.vacuum.pv31cn"


class StoredState(IntEnum):
    """Dreame state codes stored after Xiaomi values are converted."""

    SWEEPING = 1
    IDLE = 2
    PAUSED = 3
    ERROR = 4
    RETURNING = 5
    CHARGING = 6
    MOPPING = 7
    DRYING = 8
    WASHING = 9
    RETURNING_TO_WASH = 10
    BUILDING = 11
    SWEEPING_AND_MOPPING = 12
    CHARGING_COMPLETED = 13
    UPGRADING = 14
    # Below 19, so the old state enum does not relabel clean-summon.
    CLEAN_SUMMON = 15
    WASHING_PAUSED = 21
    REMOTE_CONTROL = 23
    STATION_CLEANING = 30


class StoredTask(IntEnum):
    """Dreame task-status codes stored for Xiaomi models."""

    COMPLETED = 0
    AUTO_CLEANING = 1
    ZONE_CLEANING = 2
    SEGMENT_CLEANING = 3
    SPOT_CLEANING = 4
    FAST_MAPPING = 5
    AUTO_CLEANING_PAUSED = 6


_ONE_INDEXED_PROPERTIES: Final[frozenset[str]] = frozenset(
    {"CLEANING_MODE", "SUCTION_LEVEL"}
)
_CHARGING: Final = 1
_NOT_CHARGING: Final = 2
_NOT_CHARGEABLE: Final = 3
_DOCKED_TASK_STATES: Final[frozenset[int]] = frozenset(
    {
        int(StoredState.IDLE),
        int(StoredState.CHARGING),
        int(StoredState.CHARGING_COMPLETED),
        int(StoredState.RETURNING),
        int(StoredState.WASHING),
        int(StoredState.RETURNING_TO_WASH),
        int(StoredState.DRYING),
        int(StoredState.STATION_CLEANING),
        int(StoredState.ERROR),
    }
)
_PAUSED_TASK_STATES: Final[frozenset[int]] = frozenset(
    {int(StoredState.PAUSED), int(StoredState.WASHING_PAUSED)}
)
_ACTIVE_TASK_STATES: Final[frozenset[int]] = frozenset(
    {
        int(StoredState.SWEEPING),
        int(StoredState.MOPPING),
        int(StoredState.SWEEPING_AND_MOPPING),
    }
)


@runtime_checkable
class _HasPropertyCodec(Protocol):
    """A device that carries the codec installed by the family applicator."""

    _property_codec: object


@dataclass(frozen=True, slots=True)
class XiaomiModel:
    """MIoT identity and value conversion for one Xiaomi vacuum."""

    model: str
    property_overrides: dict[str, dict[str, int]]
    action_overrides: dict[str, dict[str, int]]
    state_by_wire: dict[int, int]
    task_by_wire: dict[int, int]
    is_simple_cleaning_mode: bool = True
    should_correct_docked_activity: bool = True
    controls: tuple[XiaomiControl, ...] = ()

    def convert_incoming(self, property_name: str, value: object) -> object:
        """Map a raw property value into the Dreame value domain."""
        number = _as_int(value)
        if number is None:
            return value
        if property_name == "STATE":
            mapped = self.state_by_wire.get(number)
            return number if mapped is None else mapped
        if property_name == "TASK_STATUS":
            mapped = self.task_by_wire.get(number)
            return number if mapped is None else mapped
        if property_name == "CHARGING_STATUS" and number == _NOT_CHARGEABLE:
            return _NOT_CHARGING
        if property_name in _ONE_INDEXED_PROPERTIES and number > 0:
            return number - 1
        return number

    def convert_outgoing(self, property_name: str, value: object) -> object:
        """Map a Dreame value to the integer the robot expects on the wire."""
        if property_name not in _ONE_INDEXED_PROPERTIES or isinstance(value, bool):
            return value
        if isinstance(value, int):
            return value + 1
        return value

    def task_status_code(self, state: object, charging: object) -> int:
        """Derive task status from state, because sweep-type stays set while docked."""
        charging_code = _as_int(charging)
        if charging_code == _CHARGING:
            return int(StoredTask.COMPLETED)
        state_code = _as_int(state)
        if state_code in _DOCKED_TASK_STATES:
            return int(StoredTask.COMPLETED)
        if state_code in _PAUSED_TASK_STATES:
            return int(StoredTask.AUTO_CLEANING_PAUSED)
        if state_code in _ACTIVE_TASK_STATES:
            return int(StoredTask.AUTO_CLEANING)
        return int(StoredTask.COMPLETED)

    def build_property_transport(
        self, host: str, token: str
    ) -> MiioPropertyTransport | None:
        """Build a local property transport, or None when the cloud path remains."""
        # None is the existing cloud path. An invalid token must not raise into Dreame.
        if not host or not token:
            return None
        try:
            return MiioPropertyTransport(host, token)
        except XiaomiTransportException:
            return None

    def apply_capabilities(self, capability: object) -> None:
        """Replace catalog flags with the flags this model's map can justify."""
        names = _flag_names(self.property_overrides, self.action_overrides)
        state = vars(capability)
        for name, value in list(state.items()):
            if name.startswith("_") or not isinstance(value, bool):
                continue
            state[name] = name in names
        state["_custom_cleaning_mode"] = False
        state["_walls"] = False
        _assign_robot_type(capability, names)
        _rebuild_capability_list(capability)

    def refresh_controls(self, device: object) -> bool:
        """Poll this model's direct controls after a full property refresh."""
        return refresh_controls(device, self.controls)


def wire_map(pairs: tuple[tuple[IntEnum, IntEnum], ...]) -> dict[int, int]:
    """Build a wire-code map from named pairs."""
    return {int(wire): int(stored) for wire, stored in pairs}


def compose_addresses(
    base: Mapping[str, Mapping[str, int]],
    additions: Mapping[str, Mapping[str, int]] | None = None,
    omitted: Collection[str] | None = None,
) -> dict[str, dict[str, int]]:
    """Copy a shared address table, drop omitted names, and apply additions."""
    merged = {name: dict(address) for name, address in base.items()}
    if omitted:
        for name in omitted:
            if name not in merged:
                raise KeyError(name)
            del merged[name]
    if not additions:
        return merged
    for name, address in additions.items():
        merged[name] = dict(address)
    return merged


def compose_codes(
    base: Mapping[int, int],
    overrides: Mapping[int, int] | None = None,
    omitted: Collection[int] | None = None,
) -> dict[int, int]:
    """Copy a shared wire map, apply overrides, and drop codes the spec omits."""
    merged = {int(wire): int(stored) for wire, stored in base.items()}
    if overrides:
        for wire, stored in overrides.items():
            merged[int(wire)] = int(stored)
    if omitted:
        for wire in omitted:
            key = int(wire)
            if key not in merged:
                raise KeyError(key)
            del merged[key]
    return merged


def compose_controls(
    base: tuple[XiaomiControl, ...],
    additions: tuple[XiaomiControl, ...] = (),
    omitted: Collection[str] | None = None,
    replaced: Mapping[str, XiaomiControl] | None = None,
) -> tuple[XiaomiControl, ...]:
    """Copy a control list, drop keys, swap replacements, and append additions."""
    skipped = set(omitted) if omitted else set()
    swaps = dict(replaced) if replaced else {}
    overlap = skipped & set(swaps)
    if overlap:
        raise KeyError(next(iter(overlap)))
    present = {control.key for control in base}
    for name in skipped | set(swaps):
        if name not in present:
            raise KeyError(name)
    kept = tuple(
        swaps.get(control.key, control)
        for control in base
        if control.key not in skipped
    )
    return kept + additions


def select_controls(
    controls: tuple[XiaomiControl, ...],
    keys: tuple[str, ...],
) -> tuple[XiaomiControl, ...]:
    """Return named controls from a shared tuple, in the requested order."""
    by_key = {control.key: control for control in controls}
    chosen: list[XiaomiControl] = []
    for key in keys:
        control = by_key.get(key)
        if control is None:
            raise KeyError(key)
        chosen.append(control)
    return tuple(chosen)


def control_with_options(
    controls: tuple[XiaomiControl, ...],
    key: str,
    options: tuple[tuple[int, str], ...],
) -> XiaomiControl:
    """Copy one shared control with the value-list a single model publishes."""
    for control in controls:
        if control.key == key:
            return replace(control, options=options)
    raise KeyError(key)


def alias_model(base: XiaomiModel, model: str) -> XiaomiModel:
    """Register another model code on an unchanged record."""
    return replace(base, model=model)


def regional_variant(
    base: XiaomiModel,
    model: str,
    *,
    property_additions: Mapping[str, Mapping[str, int]] | None = None,
    property_omitted: Collection[str] | None = None,
    action_additions: Mapping[str, Mapping[str, int]] | None = None,
    action_omitted: Collection[str] | None = None,
    control_additions: tuple[XiaomiControl, ...] = (),
    control_omitted: Collection[str] | None = None,
    control_replaced: Mapping[str, XiaomiControl] | None = None,
    state_overrides: Mapping[int, int] | None = None,
    state_omitted: Collection[int] | None = None,
    task_overrides: Mapping[int, int] | None = None,
    task_omitted: Collection[int] | None = None,
) -> XiaomiModel:
    """Copy one record and apply only the addresses a regional spec changes."""
    return replace(
        base,
        model=model,
        property_overrides=compose_addresses(
            base.property_overrides, property_additions, property_omitted
        ),
        action_overrides=compose_addresses(
            base.action_overrides, action_additions, action_omitted
        ),
        state_by_wire=compose_codes(base.state_by_wire, state_overrides, state_omitted),
        task_by_wire=compose_codes(base.task_by_wire, task_overrides, task_omitted),
        controls=compose_controls(
            base.controls,
            control_additions,
            control_omitted,
            control_replaced,
        ),
    )


def controls_of(device: object) -> tuple[XiaomiControl, ...]:
    """Return the controls installed on a device, or none for other families."""
    if not isinstance(device, _HasPropertyCodec):
        return ()
    codec = device._property_codec
    if isinstance(codec, XiaomiModel):
        return codec.controls
    return ()


def control_keys(device: object, domain: str) -> frozenset[str]:
    """Return control keys that render in one Home Assistant domain."""
    return frozenset(
        control.key for control in controls_of(device) if control.domain == domain
    )


def _as_int(value: object) -> int | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return None
    return None


def _flag_names(
    properties: Mapping[str, Mapping[str, int]],
    actions: Mapping[str, Mapping[str, int]],
) -> frozenset[str]:
    """Return feature flags whose property or action is actually mapped."""
    props = frozenset(properties)
    acts = frozenset(actions)
    names = {"mijia"}
    if "SENSOR_DIRTY_LEFT" not in props:
        names.add("disable_sensor_cleaning")
    if "DND" in props or "DND_TASK" in props:
        names.add("dnd")
    if "DND_TASK" in props:
        names.add("dnd_task")
    if "CARPET_RECOGNITION" in props:
        names.add("carpet_recognition")
    if "SELF_WASH_BASE_STATUS" in props or "START_WASHING" in acts:
        names.add("self_wash_base")
    if "WASHBOARD_CLEANING_STATUS" in props:
        names.add("station_cleaning")
    if "START_AUTO_EMPTY" in acts:
        names.add("auto_empty_base")
        names.add("auto_emptying")
    if "DETERGENT_LEFT" in props and "RESET_DETERGENT" in acts:
        names.add("detergent")
    if "DRAINAGE_STATUS" in props:
        names.add("drainage")
    if "OFF_PEAK_CHARGING" in props:
        names.add("off_peak_charging")
    if "WIFI_MAP" in props:
        names.add("wifi_map")
    if "MAP_BACKUP_STATUS" in props or "BACKUP_MAP" in acts:
        names.add("backup_map")
    if "MAP_DATA" in props or "MAP_SAVING" in props:
        names.add("lidar_navigation")
    if "MULTI_FLOOR_MAP" in props:
        names.add("multi_floor_map")
    return frozenset(names)


def _assign_robot_type(capability: object, names: frozenset[str]) -> None:
    current = vars(capability).get("robot_type")
    if not isinstance(current, IntEnum):
        return
    kind = type(current)
    if "self_wash_base" in names and "mop_pad_lifting" in names:
        chosen = kind["SWEEPING_AND_MOPPING"]
    elif "self_wash_base" in names:
        chosen = kind["MOPPING"]
    else:
        # Lidar hardware. Map features stay off until a map property is mapped.
        chosen = kind["LIDAR"]
    vars(capability)["robot_type"] = chosen


def _rebuild_capability_list(capability: object) -> None:
    state = vars(capability)
    names = [
        key
        for key, value in state.items()
        if not callable(value) and not key.startswith("_") and value is True
    ]
    if capability.custom_cleaning_mode:
        names.append("custom_cleaning_mode")
    if capability.cruising:
        names.append("cruising")
    if capability.map:
        names.append("map")
    if capability.walls:
        names.append("walls")
    state["list"] = names

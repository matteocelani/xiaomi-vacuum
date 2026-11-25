"""Apply a Xiaomi codec to a Dreame vacuum device."""

from __future__ import annotations

from collections.abc import Callable
import logging
import time
from typing import Protocol, cast, runtime_checkable
import zlib

from .exceptions import DeviceException
from .map import DreameVacuumMapDecoder
from .types import DreameVacuumAction, DreameVacuumProperty

_LOGGER = logging.getLogger(__name__)


@runtime_checkable
class _RefreshableControls(Protocol):
    """A codec that polls its own controls after a full property refresh."""

    controls: tuple[object, ...]

    def refresh_controls(self, device: object) -> bool:
        """Poll the codec's controls and report whether a value changed."""


@runtime_checkable
class _PollsProperties(Protocol):
    """A device double or vacuum that can run a property poll."""

    def _request_properties(self, properties: object = None) -> object:
        """Read properties. A missing argument reads the full set."""


class _StoresControls(Protocol):
    """Where the control poll keeps its last values."""

    _xiaomi_values: dict[str, object]


class _ReplaceablePoll(Protocol):
    """The poll callable stored on one device, not the class method."""

    _request_properties: Callable[[object], object]


@runtime_checkable
class _NamesFaults(Protocol):
    """A codec that names fault codes instead of using the Dreame vocabulary."""

    def fault_name(self, code: object) -> str | None:
        """Return a translation key, or None when Dreame names still apply."""


class _Probe(Protocol):
    """A local transport that can try the token."""

    def probe(self) -> bool:
        """Return whether the robot accepts the token."""


class _PropertyProtocol(Protocol):
    """Property transport and one map read."""

    property_transport: object | None

    def get_properties(self, items: list[dict[str, object]]) -> object:
        """Read one batch of properties."""


class _MapStatus(Protocol):
    """Status fields the published map frame is stored on."""

    _xiaomi_map_raw: str | None
    _xiaomi_map: object


class _MapManager(Protocol):
    """The map manager slots a family replaces."""

    action_mapping: object
    property_mapping: object


class _LoadedCapability(Protocol):
    """A capability table that knows whether the catalog row was loaded."""

    loaded: bool


class _FamilyDevice(Protocol):
    """The device fields apply_family reads and writes."""

    property_mapping: dict[DreameVacuumProperty, dict[str, int]]
    action_mapping: dict[DreameVacuumAction, dict[str, int]]
    _property_codec: object
    _protocol: _PropertyProtocol
    capability: _LoadedCapability
    host: object
    token: object
    _map_manager: _MapManager | None
    status: _MapStatus
    _xiaomi_values: dict[str, object]

    def _request_properties(self, properties: object = None) -> object:
        """Read properties. A missing argument reads the full set."""


class _FamilyRecord(Protocol):
    """A model record apply_family can install."""

    model: str
    property_overrides: dict[str, dict[str, int]]
    action_overrides: dict[str, dict[str, int]]
    map_address: tuple[int, int] | None

    def apply_capabilities(self, capability: object) -> None:
        """Replace catalog flags from this model's map."""

    def build_property_transport(self, host: str, token: str) -> _Probe | None:
        """Build a local property transport."""

    def refresh_controls(self, device: object) -> bool:
        """Poll the codec's controls."""


def family_fault_name(device: _FamilyDevice, code: object) -> str | None:
    """Return a family fault translation key, or None when the codec has no table."""
    codec = device._property_codec
    if not isinstance(codec, _NamesFaults):
        return None
    named = codec.fault_name(code)
    if not isinstance(named, str) or not named:
        return None
    return named


def apply_family(
    device: _FamilyDevice, family: _FamilyRecord, *, probe: bool = True
) -> None:
    """Install explicit maps, then keep a local transport so a later poll can retry."""
    property_overrides = family.property_overrides
    action_overrides = family.action_overrides
    device.property_mapping = _explicit_property_map(property_overrides)
    device.action_mapping = _explicit_action_map(action_overrides)
    device._property_codec = family
    _bind_map_manager(device)
    transport = _property_transport(device, family)
    if transport is None:
        device._protocol.property_transport = None
    else:
        # Keep the transport when the robot is offline so a later poll can retry.
        # probe is false on the event loop. connect_device probes from the executor.
        if probe and not transport.probe():
            _LOGGER.warning(
                "Local miIO probe failed for model %s; property calls will retry",
                family.model,
            )
        device._protocol.property_transport = transport
    # Load already copied a Dreame catalog row. Replace it when the row is stale.
    capability = device.capability
    if capability.loaded:
        family.apply_capabilities(capability)
    _install_control_refresh(device, family)
    _LOGGER.info("Applied family codec for model %s", family.model)


def _install_control_refresh(device: _FamilyDevice, family: object) -> None:
    """Poll model controls after a full refresh without changing other models."""
    # Spec doubles and non-Xiaomi codecs have no control table. Address-test
    # devices also have no property poll, so they are not wrapped.
    if not isinstance(family, _RefreshableControls) or not family.controls:
        return
    if not isinstance(device, _PollsProperties):
        return
    # The poll check does not require a value store. This assignment creates it.
    cast(_StoresControls, device)._xiaomi_values = {}
    original = device._request_properties

    def request_properties(properties: object = None) -> object:
        changed = original(properties)
        if properties:
            return changed
        try:
            refreshed = family.refresh_controls(device)
            loaded = _load_published_map(device, family)  # family still has map_address
        except (DeviceException, OSError, ValueError, TypeError, zlib.error):
            # A bad control or map frame must not fail the property poll.
            _LOGGER.debug("Xiaomi control refresh failed", exc_info=True)
            return changed
        if loaded:
            return True
        if refreshed:
            return True
        return changed

    # The poll method is an instance slot. The class method stays for every other device.
    slot = cast(_ReplaceablePoll, device)
    slot._request_properties = request_properties


def _load_published_map(device: _FamilyDevice, family: object) -> bool:
    """Decode a published map frame into the status the camera renders."""
    address = getattr(family, "map_address", None)
    if not isinstance(address, tuple) or len(address) != 2:
        return False
    siid, piid = address
    if not isinstance(siid, int) or not isinstance(piid, int):
        return False
    result = device._protocol.get_properties(
        [{"did": f"{siid}.{piid}", "siid": siid, "piid": piid}]
    )
    if not isinstance(result, list) or not result:
        return False
    item = result[0]
    if not isinstance(item, dict) or item.get("code") != 0:
        return False
    value = item.get("value")
    if not isinstance(value, str) or not value:
        return False
    # The frame is fetched every poll. Decode it only when the bytes changed.
    if getattr(device.status, "_xiaomi_map_raw", None) == value:
        return False
    decoded = DreameVacuumMapDecoder.decode_map(value)
    current = decoded[0] if isinstance(decoded, tuple) else None
    if current is None:
        return False
    if getattr(current, "last_updated", None) is None:
        current.last_updated = time.time()
    device.status._xiaomi_map_raw = value
    device.status._xiaomi_map = current
    return True


def _property_transport(device: _FamilyDevice, family: _FamilyRecord) -> _Probe | None:
    host = device.host
    token = device.token
    if not isinstance(host, str) or not host or not isinstance(token, str) or not token:
        return None
    return family.build_property_transport(host, token)


def _bind_map_manager(device: _FamilyDevice) -> None:
    manager = device._map_manager
    if manager is None:
        return
    if _family_exposes_map(device):
        manager.action_mapping = device.action_mapping
        manager.property_mapping = device.property_mapping
        return
    device._map_manager = None


def _family_exposes_map(device: _FamilyDevice) -> bool:
    properties = device.property_mapping
    actions = device.action_mapping
    return (
        DreameVacuumProperty.MAP_DATA in properties
        or DreameVacuumProperty.OBJECT_NAME in properties
        or DreameVacuumAction.REQUEST_MAP in actions
    )


def _explicit_property_map(
    overrides: dict[str, dict[str, int]],
) -> dict[DreameVacuumProperty, dict[str, int]]:
    # Dreame defaults are a different product. An omitted Xiaomi property is not read.
    merged: dict[DreameVacuumProperty, dict[str, int]] = {}
    for name, mapping in overrides.items():
        if "siid" not in mapping or "piid" not in mapping:
            continue
        try:
            prop = DreameVacuumProperty[name]
        except KeyError as err:
            raise DeviceException(f"unknown property name {name}") from err
        merged[prop] = mapping
    return merged


def _explicit_action_map(
    overrides: dict[str, dict[str, int]],
) -> dict[DreameVacuumAction, dict[str, int]]:
    merged: dict[DreameVacuumAction, dict[str, int]] = {}
    for name, mapping in overrides.items():
        if "siid" not in mapping or "aiid" not in mapping:
            continue
        try:
            action = DreameVacuumAction[name]
        except KeyError as err:
            raise DeviceException(f"unknown action name {name}") from err
        merged[action] = mapping
    return merged

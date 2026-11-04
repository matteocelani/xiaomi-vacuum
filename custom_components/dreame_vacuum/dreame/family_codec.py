"""Apply a Xiaomi codec to a Dreame vacuum device."""

from __future__ import annotations

import logging
from typing import Protocol, runtime_checkable

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


@runtime_checkable
class _NamesFaults(Protocol):
    """A codec that names fault codes instead of using the Dreame vocabulary."""

    def fault_name(self, code: object) -> str | None:
        """Return a translation key, or None when Dreame names still apply."""


def family_fault_name(device: object, code: object) -> str | None:
    """Return a family fault translation key, or None when the codec has no table."""
    codec = device._property_codec
    if not isinstance(codec, _NamesFaults):
        return None
    named = codec.fault_name(code)
    if not isinstance(named, str) or not named:
        return None
    return named


def apply_family(device: object, family: object) -> None:
    """Install explicit maps, then keep a local transport so a later poll can retry."""
    property_overrides = family.property_overrides
    action_overrides = family.action_overrides
    device.property_mapping = _explicit_property_map(property_overrides)
    device.action_mapping = _explicit_action_map(action_overrides)
    device._property_codec = family
    if device._map_manager is not None:
        device._map_manager.action_mapping = device.action_mapping
    transport = _property_transport(device, family)
    if transport is None:
        device._protocol.property_transport = None
    else:
        # Keep the transport when the robot is offline so a later poll can retry.
        if not transport.probe():
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


def _install_control_refresh(device: object, family: object) -> None:
    """Poll model controls after a full refresh without changing other models."""
    # Spec doubles and non-Xiaomi codecs have no control table. Address-test
    # devices also have no property poll, so they are not wrapped.
    if not isinstance(family, _RefreshableControls) or not family.controls:
        return
    if not isinstance(device, _PollsProperties):
        return
    device._xiaomi_values = {}
    original = device._request_properties

    def request_properties(properties: object = None) -> object:
        changed = original(properties)
        if properties:
            return changed
        if family.refresh_controls(device):
            return True
        return changed

    device._request_properties = request_properties


def _property_transport(device: object, family: object) -> object | None:
    host = device.host
    token = device.token
    if not isinstance(host, str) or not host or not isinstance(token, str) or not token:
        return None
    return family.build_property_transport(host, token)


def _explicit_property_map(
    overrides: dict[str, dict[str, int]],
) -> dict[DreameVacuumProperty, dict[str, int]]:
    # Dreame defaults are a different product. An omitted Xiaomi property is not read.
    merged: dict[DreameVacuumProperty, dict[str, int]] = {}
    for name, mapping in overrides.items():
        if "siid" not in mapping or "piid" not in mapping:
            continue
        merged[DreameVacuumProperty[name]] = mapping
    return merged


def _explicit_action_map(
    overrides: dict[str, dict[str, int]],
) -> dict[DreameVacuumAction, dict[str, int]]:
    merged: dict[DreameVacuumAction, dict[str, int]] = {}
    for name, mapping in overrides.items():
        if "siid" not in mapping or "aiid" not in mapping:
            continue
        merged[DreameVacuumAction[name]] = mapping
    return merged

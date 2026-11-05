"""Codec application onto a Dreame device without opening a socket."""

from __future__ import annotations

from custom_components.dreame_vacuum.dreame.family_codec import apply_family
from custom_components.dreame_vacuum.dreame.types import (
    DID,
    DreameVacuumAction,
    DreameVacuumProperty,
)
from custom_components.dreame_vacuum.xiaomi import resolve_family
from custom_components.dreame_vacuum.xiaomi.mapping import (
    MODEL_ROBOT_VACUUM_5,
    MODEL_S20_PLUS,
    MODEL_X20_MAX,
)


class _MapManager:
    def __init__(self) -> None:
        self.action_mapping = None


class _Protocol:
    def __init__(self) -> None:
        self.property_transport = "unset"


class _Capability:
    loaded = False


class _Device:
    def __init__(self, host: str = "", token: str = "") -> None:
        self.property_mapping = None
        self.action_mapping = None
        self._property_codec = None
        self._map_manager = _MapManager()
        self._protocol = _Protocol()
        self.host = host
        self.token = token
        self.capability = _Capability()


class _Transport:
    def __init__(self, answers: bool) -> None:
        self.answers = answers
        self.probed = False

    def probe(self) -> bool:
        self.probed = True
        return self.answers


class _Family:
    def __init__(self, transport: _Transport | None) -> None:
        self.model = MODEL_S20_PLUS
        self.property_overrides = {"VOLUME": {"siid": 4, "piid": 2}}
        self.action_overrides = {"LOCATE": {}}
        self.transport = transport
        self.built = False

    def build_property_transport(self, host: str, token: str) -> _Transport | None:
        self.built = True
        assert host == "127.0.0.1"
        assert token == "00" * 16
        return self.transport


def test_apply_family_installs_only_explicit_x20_max_addresses():
    family = resolve_family(MODEL_X20_MAX)
    assert family is not None
    device = _Device()

    def original(properties: object = None) -> bool:
        del properties
        return False

    device._request_properties = original
    apply_family(device, family)
    assert device._request_properties is not original
    assert device._xiaomi_values == {}
    assert device._property_codec is family
    assert device._map_manager is None
    assert device.property_mapping[DreameVacuumProperty.STATE] == {"siid": 2, "piid": 2}
    assert device.property_mapping[DreameVacuumProperty.ERROR] == {"siid": 2, "piid": 3}
    assert DreameVacuumAction.REQUEST_MAP not in device.action_mapping
    assert DreameVacuumAction.RESUME in device.action_mapping
    assert DreameVacuumProperty.STATUS not in device.property_mapping
    assert device._protocol.property_transport is None
    assert set(device.property_mapping) == {
        DreameVacuumProperty[name] for name in family.property_overrides
    }
    assert DID(2, 2, device.property_mapping) is DreameVacuumProperty.STATE
    assert DID(2, 1, device.property_mapping) is None


def test_apply_family_disables_s20_plus_map_requests():
    family = resolve_family(MODEL_S20_PLUS)
    assert family is not None
    device = _Device()

    def original(properties: object = None) -> bool:
        del properties
        return False

    device._request_properties = original
    apply_family(device, family)
    assert device._request_properties is not original
    assert device._xiaomi_values == {}
    assert DreameVacuumAction.REQUEST_MAP not in device.action_mapping
    assert DreameVacuumAction.PLAY_SOUND not in device.action_mapping
    assert DreameVacuumAction.BACKUP_MAP not in device.action_mapping
    assert family.property_overrides["STATE"] == {"siid": 2, "piid": 1}
    assert DID(2, 1, device.property_mapping) is DreameVacuumProperty.STATE
    assert DreameVacuumProperty.DND_START not in device.property_mapping


def test_apply_family_keeps_transport_when_the_probe_misses():
    answering = _Transport(True)
    family = _Family(answering)
    device = _Device("127.0.0.1", "00" * 16)
    apply_family(device, family)
    assert answering.probed is True
    assert device._protocol.property_transport is answering
    silent = _Transport(False)
    offline = _Device("127.0.0.1", "00" * 16)
    apply_family(offline, _Family(silent))
    assert silent.probed is True
    assert offline._protocol.property_transport is silent
    quiet = _Family(None)
    untouched = _Device("127.0.0.1", "00" * 16)
    apply_family(untouched, quiet)
    assert quiet.built is True
    assert untouched._protocol.property_transport is None
    skipped = _Family(_Transport(True))
    apply_family(_Device(), skipped)
    assert skipped.built is False


def test_apply_family_refreshes_robot_vacuum_5_controls_on_a_full_poll():
    family = resolve_family(MODEL_ROBOT_VACUUM_5)
    assert family is not None
    device = _Device()

    def original(properties: object = None) -> bool:
        del properties
        return False

    device._request_properties = original
    apply_family(device, family)
    device._protocol.get_properties = lambda items: [
        {"siid": item["siid"], "piid": item["piid"], "code": 0, "value": 1}
        for item in items
    ]
    assert device._request_properties([DreameVacuumProperty.STATE]) is False
    assert device._xiaomi_values == {}
    assert device._request_properties() is True
    assert device._xiaomi_values
    assert all(value == 1 for value in device._xiaomi_values.values())

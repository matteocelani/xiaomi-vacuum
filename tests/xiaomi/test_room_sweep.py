"""Room clean uses the spec action that carries a room-id string."""

from __future__ import annotations

from custom_components.xiaomi_robot_vacuum.xiaomi.exceptions import (
    XiaomiControlException,
)
from custom_components.xiaomi_robot_vacuum.xiaomi.mapping import resolve_family
from custom_components.xiaomi_robot_vacuum.xiaomi.room import (
    clean_rooms,
    supports_room_clean,
)
import pytest
from tests.virtual.fleet_catalog import robot_profiles
from tests.virtual.spec_robot import load_actions

_PREFERRED = ("start-vacuum-room-sweep", "start-room-sweep")


def test_every_model_room_sweep_matches_its_spec() -> None:
    """A model with a room-start action publishes that address and no other."""
    for profile in robot_profiles():
        if profile.submodel:
            continue
        family = resolve_family(profile.model)
        assert family is not None
        assert family.room_sweep == _spec_room_sweep(profile.document()), profile.model


def test_clean_rooms_sends_the_room_id_string() -> None:
    """The service payload is the comma-separated id list on the spec piid."""
    family = resolve_family("xiaomi.vacuum.b108gl")
    assert family is not None
    device = _Device(family)
    clean_rooms(device, [1, 2])
    assert device.protocol.calls == [(2, 13, [{"piid": 13, "value": "1,2"}])]


def test_clean_rooms_rejects_a_bad_payload_or_a_failed_action() -> None:
    """Illegal ids and a refused action never look like success."""
    family = resolve_family("xiaomi.vacuum.b108gl")
    assert family is not None
    device = _Device(family)
    clean_rooms(device, 1)
    assert device.protocol.calls[-1][2] == [{"piid": 13, "value": "1"}]
    device.protocol.result = {"code": 1}
    with pytest.raises(XiaomiControlException):
        clean_rooms(device, [1])
    silent = _Device(family)
    silent.protocol = None
    silent._protocol = None
    with pytest.raises(XiaomiControlException):
        clean_rooms(silent, [1])
    broken = _Device(family)
    broken._property_codec = _Codec((2, 13, "room"))
    assert supports_room_clean(broken) is False
    for segment_ids in ("1", [], [0], [True]):
        with pytest.raises(XiaomiControlException):
            clean_rooms(device, segment_ids)


def test_models_without_a_room_action_refuse_the_call() -> None:
    """Essential vacuums have no room-id action, so the call does not leave."""
    family = resolve_family("mijia.vacuum.v1")
    assert family is not None
    assert supports_room_clean(_Device(family)) is False
    with pytest.raises(XiaomiControlException) as caught:
        clean_rooms(_Device(family), [1])
    assert caught.value.key == "room_sweep"


class _Codec:
    def __init__(self, room_sweep: object) -> None:
        self.room_sweep = room_sweep


class _Protocol:
    def __init__(self) -> None:
        self.calls: list[tuple[int, int, object]] = []
        self.result: dict[str, int] = {"code": 0}

    def action(
        self,
        siid: int,
        aiid: int,
        parameters: object = None,
        retry_count: int = 2,
    ) -> dict[str, int]:
        del retry_count
        self.calls.append((siid, aiid, parameters))
        return self.result


class _Device:
    def __init__(self, family: object) -> None:
        self._property_codec = family
        self.protocol = _Protocol()
        self._protocol = self.protocol


def _spec_room_sweep(document: dict[str, object]) -> tuple[int, int, int] | None:
    actions = load_actions(document)
    for token in _PREFERRED:
        for action in actions.values():
            if action.token == token and len(action.inputs) == 1:
                return action.siid, action.aiid, action.inputs[0]
    return None

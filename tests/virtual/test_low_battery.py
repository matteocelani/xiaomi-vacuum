"""A reported battery of zero stays empty and blocks a low-battery command."""

from __future__ import annotations

from custom_components.xiaomi_robot_vacuum.dreame.device import DreameVacuumDevice
from custom_components.xiaomi_robot_vacuum.dreame.exceptions import (
    InvalidActionException,
)
from custom_components.xiaomi_robot_vacuum.xiaomi.mapping import resolve_family
import pytest
from tests.virtual.dreame_map_robot import DreameMapRobot
from tests.virtual.fleet_catalog import RobotProfile, robot_profiles
from tests.virtual.miio_endpoint import MiioEndpoint
from tests.virtual.spec_robot import SpecRobot
from tests.xiaomi.helpers import release_device

_TOKEN = "00" * 16
_MAC = "00:00:00:00:00:31"
_CANONICAL = tuple(profile for profile in robot_profiles() if not profile.submodel)

pytestmark = [
    pytest.mark.enable_socket,
    pytest.mark.allow_hosts(["127.0.0.1"]),
]


@pytest.mark.parametrize("profile", _CANONICAL, ids=lambda profile: profile.model)
def test_zero_battery_stays_zero_and_blocks_fast_mapping(
    profile: RobotProfile,
    socket_enabled: None,
) -> None:
    """The wire value 0 is an empty battery, not a missing one."""
    del socket_enabled
    family = resolve_family(profile.model)
    assert family is not None
    robot = SpecRobot(profile.model, profile.document(), mac=_MAC)
    robot.apply_family(family)
    battery = family.property_overrides["BATTERY_LEVEL"]
    with MiioEndpoint(robot):
        device = _device(profile.model)
        device.connect_device()
        try:
            written = robot.write(
                {"siid": battery["siid"], "piid": battery["piid"], "value": 0}
            )
            assert written["code"] == 0
            device._request_properties()
            _assert_empty(device)
        finally:
            release_device(device)


def test_dreame_zero_battery_stays_zero(socket_enabled: None) -> None:
    """The lab Dreame reports an empty battery the same way a real one does."""
    del socket_enabled
    robot = DreameMapRobot("dreame.vacuum.p2008", mac=_MAC)
    robot.publish(3, 1, 0)
    with MiioEndpoint(robot):
        device = _device("dreame.vacuum.p2008", mac=_MAC)
        device.connect_device()
        try:
            device._request_properties()
            _assert_empty(device)
        finally:
            release_device(device)


def _device(model: str, mac: str = _MAC) -> DreameVacuumDevice:
    return DreameVacuumDevice(
        "Lab",
        "127.0.0.1",
        _TOKEN,
        mac,
        account_type="mi",
        family_resolver=resolve_family,
        configured_model=model,
    )


def _assert_empty(device: DreameVacuumDevice) -> None:
    assert device.status.battery_level == 0
    assert device.status.attributes["battery"] == 0
    with pytest.raises(InvalidActionException) as caught:
        device.start_fast_mapping()
    assert caught.value.translation_key == "low_battery"

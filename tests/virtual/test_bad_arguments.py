"""A missing coordinate or shortcut id is rejected, not a crash."""

from __future__ import annotations

from custom_components.xiaomi_robot_vacuum.dreame.device import DreameVacuumDevice
from custom_components.xiaomi_robot_vacuum.dreame.exceptions import (
    DeviceException,
)
import pytest
from tests.virtual.dreame_map_robot import DreameMapRobot
from tests.virtual.miio_endpoint import MiioEndpoint
from tests.xiaomi.helpers import release_device

_TOKEN = "00" * 16
_MAC = "00:00:00:00:00:62"

pytestmark = [
    pytest.mark.enable_socket,
    pytest.mark.allow_hosts(["127.0.0.60"]),
]


def test_missing_goto_and_shortcut_arguments_are_rejected(socket_enabled: None) -> None:
    """None is not a coordinate and not a shortcut id."""
    del socket_enabled
    robot = DreameMapRobot("dreame.vacuum.p2008", mac=_MAC)
    with MiioEndpoint(robot, host="127.0.0.60"):
        device = DreameVacuumDevice(
            "Lab Dreame",
            "127.0.0.60",
            _TOKEN,
            _MAC,
            account_type="mi",
            configured_model="dreame.vacuum.p2008",
        )
        device.connect_device()
        try:
            with pytest.raises(DeviceException):
                device.go_to(None, None)
            with pytest.raises(DeviceException):
                device.start_shortcut(None)
            with pytest.raises(DeviceException):
                device.start_shortcut("")
        finally:
            release_device(device)

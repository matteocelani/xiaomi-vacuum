"""Commands issued together must not raise an unexpected error."""

from __future__ import annotations

import threading

from custom_components.xiaomi_robot_vacuum.dreame.device import DreameVacuumDevice
from custom_components.xiaomi_robot_vacuum.dreame.exceptions import (
    DeviceException,
    InvalidActionException,
    InvalidValueException,
    NotSupportedException,
    UnavailableException,
)
from custom_components.xiaomi_robot_vacuum.xiaomi.mapping import resolve_family
import pytest
from tests.virtual.fleet_catalog import robot_profiles
from tests.virtual.miio_endpoint import MiioEndpoint
from tests.virtual.spec_robot import SpecRobot
from tests.xiaomi.helpers import release_device

_TOKEN = "00" * 16
_MAC = "00:00:00:00:00:22"
_CANONICAL = tuple(profile for profile in robot_profiles() if not profile.submodel)
_EXPECTED = (
    DeviceException,
    InvalidActionException,
    InvalidValueException,
    NotSupportedException,
    UnavailableException,
)

pytestmark = [
    pytest.mark.enable_socket,
    pytest.mark.allow_hosts(["127.0.0.1"]),
]


@pytest.mark.parametrize("profile", _CANONICAL, ids=lambda profile: profile.model)
def test_overlapping_commands_stay_on_the_spec(
    profile: object, socket_enabled: None
) -> None:
    """Start, stop, pause, dock, and a poll may overlap without a new exception."""
    del socket_enabled
    model = profile.model
    family = resolve_family(model)
    assert family is not None
    robot = SpecRobot(model, profile.document(), mac=_MAC)
    robot.apply_family(family)
    unexpected: list[str] = []
    with MiioEndpoint(robot):
        device = DreameVacuumDevice(
            "Lab",
            "127.0.0.1",
            _TOKEN,
            _MAC,
            account_type="mi",
            family_resolver=resolve_family,
            configured_model=model,
        )
        device.connect_device()
        try:
            _hammer(device, unexpected)
        finally:
            release_device(device)
    assert unexpected == []


def _hammer(device: DreameVacuumDevice, unexpected: list[str]) -> None:
    def run(name: str, action: object) -> None:
        for _ in range(8):
            try:
                action()
            except _EXPECTED:
                continue
            except Exception as exc:  # noqa: BLE001 - record anything outside device errors
                unexpected.append(f"{name} {type(exc).__name__}: {exc}")

    threads = [
        threading.Thread(target=run, args=("start", device.start)),
        threading.Thread(target=run, args=("stop", device.stop)),
        threading.Thread(target=run, args=("pause", device.pause)),
        threading.Thread(target=run, args=("dock", device.return_to_base)),
        threading.Thread(target=run, args=("poll", device._request_properties)),
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=30)

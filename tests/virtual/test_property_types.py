"""A non-numeric state or battery must not crash the status read."""

from __future__ import annotations

from custom_components.xiaomi_robot_vacuum.dreame.device import DreameVacuumDevice
from custom_components.xiaomi_robot_vacuum.dreame.types import (
    DreameVacuumProperty,
    DreameVacuumState,
)
from custom_components.xiaomi_robot_vacuum.xiaomi.mapping import resolve_family
import pytest
from tests.virtual.fleet_catalog import robot_profiles
from tests.virtual.miio_endpoint import MiioEndpoint
from tests.virtual.spec_robot import SpecRobot
from tests.xiaomi.helpers import release_device

_TOKEN = "00" * 16
_MAC = "00:00:00:00:00:71"
_HOST = "127.0.0.60"
_MODELS = (
    "xiaomi.vacuum.b108gl",
    "xiaomi.vacuum.b112",
    "mijia.vacuum.v1",
    "xiaomi.vacuum.ov31gl",
    "xiaomi.vacuum.qv41gl",
    "xiaomi.vacuum.pv32cn",
)

pytestmark = [
    pytest.mark.enable_socket,
    pytest.mark.allow_hosts(["127.0.0.60"]),
]


@pytest.mark.parametrize("model", _MODELS)
def test_non_numeric_state_and_battery_stay_readable(
    model: str, socket_enabled: None
) -> None:
    """Strings where a code or a percent is expected become unknown, not an exception."""
    del socket_enabled
    profile = next(
        item for item in robot_profiles() if item.model == model and not item.submodel
    )
    family = resolve_family(model)
    assert family is not None
    robot = SpecRobot(model, profile.document(), mac=_MAC)
    robot.apply_family(family)
    with MiioEndpoint(robot, host=_HOST):
        device = DreameVacuumDevice(
            "Lab",
            _HOST,
            _TOKEN,
            _MAC,
            account_type="mi",
            family_resolver=resolve_family,
            configured_model=model,
        )
        device.connect_device()
        try:
            device.data[DreameVacuumProperty.STATE.value] = "nope"
            assert device.status.state is DreameVacuumState.UNKNOWN
            device.data[DreameVacuumProperty.STATE.value] = "6"
            assert isinstance(device.status.state, DreameVacuumState)
            device.data[DreameVacuumProperty.BATTERY_LEVEL.value] = "nope"
            assert device.status.battery_level == 100
            device.data[DreameVacuumProperty.BATTERY_LEVEL.value] = "0"
            assert device.status.battery_level == 0
            device.data[DreameVacuumProperty.VOLUME.value] = "nope"
            assert device.status.volume == 0
            assert isinstance(device.status.attributes, dict)
        finally:
            release_device(device)

"""One bad token in the fault list must not erase a real fault."""

from __future__ import annotations

from custom_components.xiaomi_robot_vacuum.dreame.device import DreameVacuumDevice
from custom_components.xiaomi_robot_vacuum.dreame.types import (
    DreameVacuumErrorCode,
    DreameVacuumProperty,
)
from custom_components.xiaomi_robot_vacuum.xiaomi.mapping import resolve_family
import pytest
from tests.virtual.fleet_catalog import robot_profiles
from tests.virtual.miio_endpoint import MiioEndpoint
from tests.virtual.spec_robot import SpecRobot
from tests.xiaomi.helpers import release_device

_TOKEN = "00" * 16
_MAC = "00:00:00:00:00:74"
_HOST = "127.0.0.60"

pytestmark = [
    pytest.mark.enable_socket,
    pytest.mark.allow_hosts(["127.0.0.60"]),
]


def test_a_bad_fault_token_keeps_the_known_code(socket_enabled: None) -> None:
    """``1,nope`` still reports the wheel-drop fault."""
    del socket_enabled
    model = "xiaomi.vacuum.b108gl"
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
            device.data[DreameVacuumProperty.FAULTS.value] = "1,nope,999"
            device._faults_changed()
            assert device.status.faults == [DreameVacuumErrorCode.DROP.value]
            device.status.faults = [DreameVacuumErrorCode.DROP.value, 999]
            assert device.status.attributes["faults"][999] == "Unknown"
            assert device.status.attributes["faults"][1] == "Drop"
        finally:
            release_device(device)

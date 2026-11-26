"""Drive every canonical model through the spec robot."""

from __future__ import annotations

from custom_components.xiaomi_robot_vacuum.dreame.device import DreameVacuumDevice
from custom_components.xiaomi_robot_vacuum.dreame.exceptions import (
    InvalidActionException,
    NotSupportedException,
    UnavailableException,
)
from custom_components.xiaomi_robot_vacuum.dreame.types import (
    DreameVacuumProperty,
    DreameVacuumState,
)
from custom_components.xiaomi_robot_vacuum.xiaomi.mapping import resolve_family
from custom_components.xiaomi_robot_vacuum.xiaomi.model import StoredState
from custom_components.xiaomi_robot_vacuum.xiaomi.schedule import (
    SCHEDULE_MODELS,
    add_schedule,
)
import pytest
from tests.virtual.fleet_catalog import RobotProfile, robot_profiles
from tests.virtual.miio_endpoint import MiioEndpoint
from tests.virtual.spec_robot import SpecRobot
from tests.xiaomi.helpers import release_device

_TOKEN = "00" * 16
_MAC = "00:00:00:00:00:00"
_CANONICAL = tuple(profile for profile in robot_profiles() if not profile.submodel)

pytestmark = [
    pytest.mark.enable_socket,
    pytest.mark.allow_hosts(["127.0.0.1"]),
]


@pytest.mark.parametrize("profile", _CANONICAL, ids=lambda profile: profile.model)
def test_model_cycle_covers_clean_dock_fault_and_consumables(
    profile: RobotProfile,
    socket_enabled: None,
) -> None:
    del socket_enabled
    """Start, dock, and a fault stay on addresses this spec publishes."""
    family = resolve_family(profile.model)
    assert family is not None
    robot = SpecRobot(profile.model, profile.document(), mac=_MAC)
    robot.apply_family(family)
    with MiioEndpoint(robot):
        device = _device(profile.model)
        device.connect_device()
        try:
            assert int(device.status.state) == int(DreameVacuumState.CHARGING)
            _assert_consumables(device, family.property_overrides)
            _clean_and_dock(device, family.action_overrides)
            device._request_properties()
            assert int(device.status.state) == int(DreameVacuumState.CHARGING)
            _try_cleaning_mode(device, family.property_overrides)
            if profile.model in SCHEDULE_MODELS:
                add_schedule(
                    device,
                    {
                        "enable": 1,
                        "day": 1,
                        "hour": 8,
                        "minute": 30,
                        "repeat": 0,
                    },
                )
            assert robot.set_fault() is not None or _has_error_wire(
                family.state_by_wire
            )
            if _has_error_wire(family.state_by_wire):
                robot.set_stored(StoredState.ERROR)
                device._request_properties()
                assert int(device.status.state) == int(DreameVacuumState.ERROR)
        finally:
            release_device(device)
    spec_properties = set(robot.properties)
    spec_actions = set(robot.actions_by_address)
    assert set(robot.actions) <= spec_actions
    assert {(siid, piid) for siid, piid, _value in robot.writes} <= spec_properties


def _device(model: str) -> DreameVacuumDevice:
    return DreameVacuumDevice(
        "Lab",
        "127.0.0.1",
        _TOKEN,
        _MAC,
        account_type="mi",
        family_resolver=resolve_family,
        configured_model=model,
    )


def _clean_and_dock(
    device: DreameVacuumDevice, actions: dict[str, dict[str, int]]
) -> None:
    device.start()
    device._request_properties()
    assert int(device.status.state) == int(DreameVacuumState.SWEEPING)
    if "PAUSE" in actions:
        device.pause()
        device._request_properties()
        assert int(device.status.state) == int(DreameVacuumState.PAUSED)
        device.start()
    else:
        with pytest.raises(InvalidActionException):
            device.pause()
    device.return_to_base()


def _assert_consumables(
    device: DreameVacuumDevice, overrides: dict[str, dict[str, int]]
) -> None:
    for name in overrides:
        if not name.endswith("_LEFT"):
            continue
        value = device.data.get(DreameVacuumProperty[name])
        assert isinstance(value, int)
        assert 0 <= value <= 100


def _try_cleaning_mode(
    device: DreameVacuumDevice, overrides: dict[str, dict[str, int]]
) -> None:
    if "CLEANING_MODE" not in overrides:
        return
    current = device.status.cleaning_mode
    if current is None:
        return
    try:
        device.set_cleaning_mode(int(current))
    except (NotSupportedException, UnavailableException):
        return


def _has_error_wire(state_by_wire: dict[int, int]) -> bool:
    return int(StoredState.ERROR) in state_by_wire.values()

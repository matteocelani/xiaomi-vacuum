"""Drive both models through a loopback miIO device and record every action."""

from __future__ import annotations

from custom_components.dreame_vacuum.dreame.device import DreameVacuumDevice
from custom_components.dreame_vacuum.dreame.exceptions import InvalidActionException
from custom_components.dreame_vacuum.dreame.types import (
    DreameVacuumProperty,
    DreameVacuumState,
)
from custom_components.dreame_vacuum.xiaomi import (
    MODEL_E5,
    MODEL_E10,
    MODEL_E10C,
    MODEL_E12,
    MODEL_H50,
    MODEL_H50_PRO,
    MODEL_H50_PRO_ROLLER,
    MODEL_H50_ROLLER,
    MODEL_MIJIA_3C,
    MODEL_MIJIA_5_PRO,
    MODEL_MIJIA_5C,
    MODEL_MIJIA_6_MAX,
    MODEL_MIJIA_6_PRO,
    MODEL_MIJIA_7_MAX,
    MODEL_MIJIA_7C,
    MODEL_MIJIA_H40,
    MODEL_MIJIA_M30,
    MODEL_MIJIA_M30_PRO,
    MODEL_MIJIA_ROBOT_VACUUM_4,
    MODEL_MIJIA_ROBOT_VACUUM_5,
    MODEL_MIJIA_ROBOT_VACUUM_6,
    MODEL_MIJIA_SWEEP_MOP_2,
    MODEL_MIJIA_SWEEP_MOP_3,
    MODEL_ROBOT_VACUUM_5_PRO,
    MODEL_ROBOT_VACUUM_6,
    MODEL_ROBOT_VACUUM_6_MAX,
    MODEL_ROBOT_VACUUM_6_PRO,
    MODEL_S12,
    MODEL_S20,
    MODEL_S60,
    MODEL_S60_PLUS,
    MODEL_T12,
    MODEL_X20,
    MODEL_X20_PRO,
    resolve_family,
)
from custom_components.dreame_vacuum.xiaomi.mapping import (
    MODEL_H40,
    MODEL_MIJIA_M40_S,
    MODEL_ROBOT_VACUUM_5,
    MODEL_S20_PLUS,
    MODEL_S40,
    MODEL_S40_PRO,
    MODEL_S40C,
    MODEL_X20_MAX,
)
import pytest
from tests.xiaomi.helpers import FakeMiio, release_device

_TOKEN = "00" * 16
_MAC = "00:00:00:00:00:00"
_FORBIDDEN = {(7, 2), (6, 3), (15, 1), (19, 1), (20, 1), (10, 7), (18, 1)}

pytestmark = [
    pytest.mark.enable_socket,
    pytest.mark.allow_hosts(["127.0.0.1"]),
]


def test_loopback_device_start_pause_resume_and_dock_send_only_mapped_actions(
    socket_enabled: None,
) -> None:
    for model in (
        MODEL_S20_PLUS,
        MODEL_X20_MAX,
        MODEL_ROBOT_VACUUM_5,
        MODEL_S40_PRO,
        MODEL_S40,
        MODEL_H40,
        MODEL_H50,
        MODEL_H50_PRO,
        MODEL_S40C,
        MODEL_ROBOT_VACUUM_5_PRO,
        MODEL_ROBOT_VACUUM_6,
        MODEL_ROBOT_VACUUM_6_MAX,
        MODEL_ROBOT_VACUUM_6_PRO,
        MODEL_S60,
        MODEL_S60_PLUS,
        MODEL_H50_PRO_ROLLER,
        MODEL_H50_ROLLER,
        MODEL_X20_PRO,
        MODEL_E5,
        MODEL_MIJIA_ROBOT_VACUUM_6,
        MODEL_MIJIA_7C,
        MODEL_MIJIA_M40_S,
        MODEL_MIJIA_5_PRO,
        MODEL_MIJIA_5C,
        MODEL_MIJIA_M30,
        MODEL_MIJIA_6_MAX,
        MODEL_MIJIA_6_PRO,
        MODEL_MIJIA_7_MAX,
        MODEL_MIJIA_H40,
        MODEL_MIJIA_M30_PRO,
        MODEL_MIJIA_ROBOT_VACUUM_4,
        MODEL_MIJIA_ROBOT_VACUUM_5,
    ):
        family = resolve_family(model)
        assert family is not None
        actions = family.action_overrides
        with FakeMiio(model) as fake:
            device = DreameVacuumDevice(
                "Sim",
                "127.0.0.1",
                _TOKEN,
                _MAC,
                account_type="mi",
                family_resolver=resolve_family,
            )
            device.connect_device()
            try:
                assert device.info is not None
                assert device.info.model == model
                assert int(device.status.state) == int(DreameVacuumState.CHARGING)
                device.start()
                device._request_properties()
                assert int(device.status.state) == int(DreameVacuumState.SWEEPING)
                device.pause()
                device._request_properties()
                assert int(device.status.state) == int(DreameVacuumState.PAUSED)
                device.start()
                device.return_to_base()
            finally:
                release_device(device)
        assert fake.actions == [
            (actions["START"]["siid"], actions["START"]["aiid"]),
            (actions["PAUSE"]["siid"], actions["PAUSE"]["aiid"]),
            (actions["RESUME"]["siid"], actions["RESUME"]["aiid"]),
            (actions["CHARGE"]["siid"], actions["CHARGE"]["aiid"]),
        ]
        assert not set(fake.actions) & _FORBIDDEN
        assert DreameVacuumProperty.STATUS not in device.property_mapping
        assert (5, 2) not in {
            (item["siid"], item["piid"]) for item in device.property_mapping.values()
        }


def test_sweep_family_starts_and_returns_without_pause(socket_enabled: None) -> None:
    """E10 has no pause action, so a pause press is not sent."""
    del socket_enabled
    for model in (
        MODEL_E10,
        MODEL_E12,
        MODEL_E10C,
        MODEL_S20,
        MODEL_X20,
        MODEL_S12,
        MODEL_T12,
        MODEL_MIJIA_SWEEP_MOP_2,
        MODEL_MIJIA_SWEEP_MOP_3,
        MODEL_MIJIA_3C,
    ):
        family = resolve_family(model)
        assert family is not None
        actions = family.action_overrides
        with FakeMiio(model) as fake:
            device = DreameVacuumDevice(
                "Sim",
                "127.0.0.1",
                _TOKEN,
                _MAC,
                account_type="mi",
                family_resolver=resolve_family,
            )
            device.connect_device()
            try:
                assert int(device.status.state) == int(DreameVacuumState.CHARGING)
                device.start()
                device._request_properties()
                assert int(device.status.state) == int(DreameVacuumState.SWEEPING)
                with pytest.raises(InvalidActionException):
                    device.pause()
                device._request_properties()
                assert int(device.status.state) == int(DreameVacuumState.SWEEPING)
                device.return_to_base()
                device._request_properties()
                assert int(device.status.state) == int(DreameVacuumState.CHARGING)
            finally:
                release_device(device)
        assert fake.actions == [
            (actions["START"]["siid"], actions["START"]["aiid"]),
            (actions["CHARGE"]["siid"], actions["CHARGE"]["aiid"]),
        ]
        assert not set(fake.actions) & _FORBIDDEN

"""Property polls do not log every value at info."""

from __future__ import annotations

import logging

from custom_components.xiaomi_robot_vacuum.dreame.device import DreameVacuumDevice
from custom_components.xiaomi_robot_vacuum.xiaomi.mapping import resolve_family
import pytest
from tests.virtual.fleet_catalog import robot_profiles
from tests.virtual.miio_endpoint import MiioEndpoint
from tests.virtual.spec_robot import SpecRobot
from tests.xiaomi.helpers import release_device

_TOKEN = "00" * 16
_MAC = "00:00:00:00:00:00"

pytestmark = [
    pytest.mark.enable_socket,
    pytest.mark.allow_hosts(["127.0.0.1"]),
]


def test_property_refresh_stays_at_debug(
    socket_enabled: None, caplog: pytest.LogCaptureFixture
) -> None:
    """A full poll must not emit one info line per property."""
    del socket_enabled
    profile = next(
        item
        for item in robot_profiles()
        if item.model == "mijia.vacuum.v1" and not item.submodel
    )
    family = resolve_family(profile.model)
    assert family is not None
    robot = SpecRobot(profile.model, profile.document(), mac=_MAC)
    robot.apply_family(family)
    with MiioEndpoint(robot):
        device = DreameVacuumDevice(
            "Lab",
            "127.0.0.1",
            _TOKEN,
            _MAC,
            account_type="mi",
            family_resolver=resolve_family,
            configured_model=profile.model,
        )
        with caplog.at_level(logging.INFO):
            device.connect_device()
        try:
            added = [
                record
                for record in caplog.records
                if record.levelno >= logging.INFO and "Property " in record.message
            ]
            assert added == []
        finally:
            release_device(device)

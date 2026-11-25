"""Local miIO failure falls through to the spec robot's cloud client."""

from __future__ import annotations

from custom_components.xiaomi_robot_vacuum.dreame.protocol import DreameVacuumProtocol
from custom_components.xiaomi_robot_vacuum.xiaomi.mapping import resolve_family
from custom_components.xiaomi_robot_vacuum.xiaomi.transport import MiioPropertyTransport
import pytest
from tests.virtual.cloud_client import CloudPropertyClient
from tests.virtual.fleet_catalog import RobotProfile, robot_profiles
from tests.virtual.miio_endpoint import MiioEndpoint
from tests.virtual.spec_robot import SpecRobot

_CLIENT_TOKEN = "00" * 16
_SERVER_TOKEN = "11" * 16
_PROFILES = robot_profiles()

pytestmark = [
    pytest.mark.enable_socket,
    pytest.mark.allow_hosts(["127.0.0.1"]),
]


@pytest.mark.parametrize("profile", _PROFILES, ids=lambda profile: profile.spec_file)
def test_rejected_local_token_reads_the_same_spec_over_cloud(
    profile: RobotProfile,
    socket_enabled: None,
) -> None:
    del socket_enabled
    """A bad local token does not change the values the cloud client returns."""
    family = resolve_family(profile.model)
    assert family is not None
    robot = SpecRobot(profile.model, profile.document(), strict=profile.submodel)
    robot.apply_family(family)
    state = family.property_overrides["STATE"]
    battery = family.property_overrides["BATTERY_LEVEL"]
    with MiioEndpoint(robot, token=_SERVER_TOKEN):
        protocol = DreameVacuumProtocol(
            "127.0.0.1",
            _CLIENT_TOKEN,
            username="lab",
            password="lab",
            country="de",
            prefer_cloud=True,
            account_type="mi",
        )
        cloud = CloudPropertyClient(robot)
        protocol.device_cloud = cloud
        protocol.property_transport = MiioPropertyTransport(
            "127.0.0.1",
            _CLIENT_TOKEN,
            timeout=0.3,
        )
        result = protocol.get_properties(
            [
                {"did": "", "siid": state["siid"], "piid": state["piid"]},
                {"did": "", "siid": battery["siid"], "piid": battery["piid"]},
            ]
        )
    assert isinstance(result, list)
    assert {item["value"] for item in result if isinstance(item, dict)} >= {
        robot.value(state["siid"], state["piid"]),
        robot.value(battery["siid"], battery["piid"]),
    }
    assert "get_properties" in cloud.calls

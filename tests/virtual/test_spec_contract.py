"""Every model spec, including older versions, drives a virtual robot."""

from __future__ import annotations

from custom_components.xiaomi_robot_vacuum.xiaomi.mapping import resolve_family
from custom_components.xiaomi_robot_vacuum.xiaomi.model import StoredState
import pytest
from tests.virtual.fleet_catalog import RobotProfile, robot_profiles
from tests.virtual.spec_robot import SpecRobot

_PROFILES = robot_profiles()
_ILLEGAL = 999_999


@pytest.mark.parametrize("profile", _PROFILES, ids=lambda profile: profile.spec_file)
def test_spec_robot_covers_properties_actions_faults_and_map(
    profile: RobotProfile,
) -> None:
    """Legal wires stick, illegal wires are refused, and the floor plan is published."""
    family = resolve_family(profile.model)
    assert family is not None
    robot = SpecRobot(
        profile.model,
        profile.document(),
        strict=profile.submodel,
    )
    robot.apply_family(family)
    _assert_initial_values(robot)
    _assert_illegal_write_is_refused(robot)
    _assert_actions(robot)
    _assert_family_addresses(profile, robot, family.property_overrides)
    _assert_map_text(robot)
    if not profile.submodel:
        robot.set_stored(StoredState.SWEEPING)
        state = family.property_overrides["STATE"]
        sweeping = [
            wire
            for wire, stored in family.state_by_wire.items()
            if stored == int(StoredState.SWEEPING)
        ]
        assert robot.value(state["siid"], state["piid"]) == min(sweeping)
    fault = robot.set_fault()
    if fault is not None:
        assert fault != 0
        error_wires = [
            wire
            for wire, stored in family.state_by_wire.items()
            if stored == int(StoredState.ERROR)
        ]
        if error_wires:
            state = family.property_overrides["STATE"]
            assert robot.value(state["siid"], state["piid"]) == min(error_wires)


def test_catalog_includes_every_supported_model_and_spec_file() -> None:
    """Canonical models and versioned spec files are all present."""
    profiles = robot_profiles()
    models = {profile.model for profile in profiles if not profile.submodel}
    assert len(models) >= 48
    assert len(profiles) >= len(models)
    files = {profile.spec_file for profile in profiles}
    assert len(files) == len(profiles)


def _assert_initial_values(robot: SpecRobot) -> None:
    for prop in robot.properties.values():
        value = robot.value(prop.siid, prop.piid)
        assert prop.allows(value), prop.token


def _assert_illegal_write_is_refused(robot: SpecRobot) -> None:
    for prop in robot.properties.values():
        if "write" not in prop.access or prop.values is None:
            continue
        if _ILLEGAL in prop.values:
            continue
        before = robot.value(prop.siid, prop.piid)
        result = robot.write({"siid": prop.siid, "piid": prop.piid, "value": _ILLEGAL})
        assert result["code"] != 0
        assert robot.value(prop.siid, prop.piid) == before
        return
    for prop in robot.properties.values():
        if "write" not in prop.access or prop.maximum is None:
            continue
        illegal = prop.maximum + 1
        before = robot.value(prop.siid, prop.piid)
        result = robot.write({"siid": prop.siid, "piid": prop.piid, "value": illegal})
        assert result["code"] != 0
        assert robot.value(prop.siid, prop.piid) == before
        return


def _assert_actions(robot: SpecRobot) -> None:
    saw_input = False
    for action in robot.actions_by_address.values():
        if not action.inputs:
            continue
        saw_input = True
        refused = robot.invoke({"siid": action.siid, "aiid": action.aiid, "in": []})
        assert refused["code"] != 0
        accepted = robot.invoke(
            {
                "siid": action.siid,
                "aiid": action.aiid,
                "in": [{"piid": piid, "value": 0} for piid in action.inputs],
            }
        )
        assert accepted["code"] == 0
        break
    if not saw_input:
        action = next(iter(robot.actions_by_address.values()))
        assert robot.invoke({"siid": action.siid, "aiid": action.aiid})["code"] == 0


def _assert_family_addresses(
    profile: RobotProfile,
    robot: SpecRobot,
    overrides: dict[str, dict[str, int]],
) -> None:
    for name, mapping in overrides.items():
        address = (mapping["siid"], mapping["piid"])
        if address in robot.properties:
            assert robot.value(*address) is not None or robot.value(*address) == ""
            continue
        if profile.submodel:
            assert robot.read({"siid": address[0], "piid": address[1]})["code"] != 0
            continue
        raise AssertionError(f"{profile.model} {name} {address} is not in the spec")


def _assert_map_text(robot: SpecRobot) -> None:
    published = False
    for prop in robot.properties.values():
        if prop.value_format != "string":
            continue
        if not any(
            word in prop.token for word in ("map", "room", "segment", "point", "zone")
        ):
            continue
        value = robot.value(prop.siid, prop.piid)
        assert isinstance(value, str) and value
        published = True
    if published:
        assert robot.floor_plan

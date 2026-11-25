"""Exercise Home Assistant services for every canonical Xiaomi model."""

from __future__ import annotations

import json
from pathlib import Path

from custom_components.xiaomi_robot_vacuum.const import (
    CONF_ACCOUNT_TYPE,
    CONF_MAC,
    CONF_NOTIFY,
    CONF_PREFER_CLOUD,
    CONF_VERSION,
    DOMAIN,
)
from custom_components.xiaomi_robot_vacuum.xiaomi.mapping import resolve_family
from custom_components.xiaomi_robot_vacuum.xiaomi.model import StoredState
from custom_components.xiaomi_robot_vacuum.xiaomi.schedule import SCHEDULE_MODELS
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry
from tests.virtual.fleet_catalog import robot_profiles
from tests.virtual.miio_endpoint import MiioEndpoint
from tests.virtual.spec_robot import SpecRobot
from tests.xiaomi.helpers import release_device

from homeassistant.const import CONF_HOST, CONF_MODEL, CONF_NAME, CONF_TOKEN
from homeassistant.core import HomeAssistant, State
from homeassistant.exceptions import HomeAssistantError

_TOKEN = "00" * 16
_ARTIFACT = Path("/opt/cursor/artifacts/virtual-lab/service-matrix.json")
_MOTION = ("start", "pause", "stop", "dock")
_SETTINGS = ("suction", "water", "mop", "dnd", "reset", "room", "schedule", "error")

pytestmark = [
    pytest.mark.ha,
    pytest.mark.enable_socket,
    pytest.mark.allow_hosts(["127.0.0.1"]),
]


async def test_every_model_service_matches_its_spec(
    hass: HomeAssistant,
    socket_enabled: None,
    enable_custom_integrations: None,
    integration_package: object,
) -> None:
    """Start, clean, and settings calls reach the robot or are absent on purpose."""
    del socket_enabled, enable_custom_integrations, integration_package
    from custom_components.xiaomi_robot_vacuum.dreame import VERSION

    matrix: dict[str, dict[str, str]] = {}
    failures: list[str] = []
    for index, profile in enumerate(
        item for item in robot_profiles() if not item.submodel
    ):
        family = resolve_family(profile.model)
        assert family is not None
        mac = f"00:00:00:00:00:{index + 1:02x}"
        robot = SpecRobot(profile.model, profile.document(), mac=mac)
        robot.apply_family(family)
        code = profile.model.rsplit(".", 1)[-1]
        with MiioEndpoint(robot):
            entry = MockConfigEntry(
                domain=DOMAIN,
                unique_id=profile.model,
                data={
                    CONF_NAME: f"Lab {code}",
                    CONF_HOST: "127.0.0.1",
                    CONF_TOKEN: _TOKEN,
                    CONF_MAC: mac,
                    CONF_MODEL: profile.model,
                    CONF_ACCOUNT_TYPE: "mi",
                },
                options={
                    CONF_PREFER_CLOUD: False,
                    CONF_NOTIFY: False,
                    CONF_VERSION: VERSION,
                },
            )
            entry.add_to_hass(hass)
            assert await hass.config_entries.async_setup(entry.entry_id)
            await hass.async_block_till_done()
            device = hass.data[DOMAIN][entry.entry_id].device
            try:
                row = await _exercise(hass, entry.entry_id, robot, family, code)
            finally:
                await hass.config_entries.async_unload(entry.entry_id)
                await hass.async_block_till_done()
                release_device(device)
        matrix[profile.model] = row
        for name, cell in row.items():
            if cell.startswith("fail"):
                failures.append(f"{profile.model} {name} {cell}")
    await hass.async_add_executor_job(_write_matrix, matrix)
    assert not failures, "\n".join(failures)


async def _exercise(
    hass: HomeAssistant,
    entry_id: str,
    robot: SpecRobot,
    family: object,
    code: str,
) -> dict[str, str]:
    row = dict.fromkeys((*_MOTION, *_SETTINGS), "absent")
    states = _owned(hass, code)
    vacuum = next((state for state in states if state.domain == "vacuum"), None)
    assert vacuum is not None, code
    row["suction"] = await _cycle_select(
        hass, entry_id, _named(states, "select", "suction_level")
    )
    row["water"] = await _cycle_select(
        hass, entry_id, _named(states, "select", "water_volume")
    )
    row["mop"] = await _cycle_mop(hass, entry_id, states)
    row["dnd"] = await _toggle_dnd(hass, entry_id, states)
    row["reset"] = await _press_resets(hass, robot, states)
    row["schedule"] = await _add_schedule(hass, vacuum.entity_id, robot, family)
    row["start"] = await _motion(
        hass, entry_id, vacuum.entity_id, robot, family, "start", "START", "cleaning"
    )
    row["pause"] = await _motion(
        hass, entry_id, vacuum.entity_id, robot, family, "pause", "PAUSE", "paused"
    )
    row["stop"] = await _motion(
        hass, entry_id, vacuum.entity_id, robot, family, "stop", "STOP", "idle"
    )
    row["dock"] = await _motion(
        hass,
        entry_id,
        vacuum.entity_id,
        robot,
        family,
        "return_to_base",
        "CHARGE",
        "docked",
    )
    row["room"] = await _room(hass, entry_id, vacuum.entity_id, robot, family)
    row["error"] = await _error(hass, entry_id, robot, vacuum.entity_id)
    del code
    return row


async def _motion(
    hass: HomeAssistant,
    entry_id: str,
    entity_id: str,
    robot: SpecRobot,
    family: object,
    service: str,
    action_name: str,
    expected: str,
) -> str:
    address = _action(family, action_name)
    if address is None:
        error = await _call(hass, "vacuum", service, {"entity_id": entity_id})
        if error is None:
            return f"fail:unmapped {action_name} was accepted"
        return "absent"
    before = len(robot.actions)
    error = await _call(hass, "vacuum", service, {"entity_id": entity_id})
    if error is not None:
        return f"fail:{error}"
    if address not in robot.actions[before:]:
        return "fail:action not sent"
    await _refresh(hass, entry_id)
    state = hass.states.get(entity_id)
    if state is None or state.state != expected:
        actual = None if state is None else state.state
        return f"fail:state {actual}"
    return "pass"


async def _cycle_select(
    hass: HomeAssistant,
    entry_id: str,
    state: State | None,
) -> str:
    if state is None:
        return "absent"
    if state.state in {"unknown", "unavailable"}:
        return f"fail:{state.state}"
    options = state.attributes.get("options")
    if not isinstance(options, list) or len(options) < 2:
        return "absent"
    option = next(item for item in options if item != state.state)
    error = await _call(
        hass,
        "select",
        "select_option",
        {"entity_id": state.entity_id, "option": option},
    )
    if error is not None:
        return f"fail:{error}"
    await _refresh(hass, entry_id)
    updated = hass.states.get(state.entity_id)
    if updated is None or updated.state != option:
        actual = None if updated is None else updated.state
        return f"fail:now {actual}"
    return "pass"


async def _cycle_mop(hass: HomeAssistant, entry_id: str, states: list[State]) -> str:
    mode = _named(states, "select", "cleaning_mode")
    if mode is None or mode.state in {"unknown", "unavailable"}:
        if mode is not None:
            return f"fail:{mode.state}"
        return "absent"
    options = mode.attributes.get("options")
    if not isinstance(options, list) or len(options) < 2:
        return "absent"
    mop_options = [item for item in options if "mop" in str(item)]
    if not mop_options:
        return "absent"
    target = next((item for item in mop_options if item != mode.state), None)
    if target is None:
        target = mop_options[0]
        other = next(item for item in options if item != mode.state)
        error = await _call(
            hass,
            "select",
            "select_option",
            {"entity_id": mode.entity_id, "option": other},
        )
        if error is not None:
            return f"fail:{error}"
        await _refresh(hass, entry_id)
    error = await _call(
        hass,
        "select",
        "select_option",
        {"entity_id": mode.entity_id, "option": target},
    )
    if error is not None:
        return f"fail:{error}"
    await _refresh(hass, entry_id)
    updated = hass.states.get(mode.entity_id)
    if updated is None or updated.state != target:
        return "fail:mode unchanged"
    return "pass"


async def _toggle_dnd(hass: HomeAssistant, entry_id: str, states: list[State]) -> str:
    switches = [
        state
        for state in states
        if state.domain == "switch"
        and ("dnd" in state.entity_id or "no_disturb" in state.entity_id)
    ]
    if not switches:
        return "absent"
    state = switches[0]
    if state.state in {"unknown", "unavailable"}:
        return f"fail:{state.state}"
    error = await _call(hass, "switch", "turn_on", {"entity_id": state.entity_id})
    if error is not None:
        return f"fail:{error}"
    await _refresh(hass, entry_id)
    updated = hass.states.get(state.entity_id)
    if updated is None or updated.state != "on":
        return "fail:still off"
    return "pass"


async def _press_resets(
    hass: HomeAssistant, robot: SpecRobot, states: list[State]
) -> str:
    buttons = [
        state
        for state in states
        if state.domain == "button" and "reset" in state.entity_id
    ]
    if not buttons:
        return "absent"
    before = len(robot.actions)
    for state in buttons:
        error = await _call(hass, "button", "press", {"entity_id": state.entity_id})
        if error is not None:
            return f"fail:{state.entity_id} {error}"
    if len(robot.actions) == before:
        return "fail:no action"
    return "pass"


async def _add_schedule(
    hass: HomeAssistant,
    entity_id: str,
    robot: SpecRobot,
    family: object,
) -> str:
    model = getattr(family, "model", None)
    if model not in SCHEDULE_MODELS:
        error = await _call(
            hass,
            DOMAIN,
            "xiaomi_add_schedule",
            {
                "entity_id": entity_id,
                "enable": True,
                "day": 1,
                "hour": 8,
                "minute": 30,
                "repeat": False,
            },
        )
        if error is None:
            return "fail:schedule accepted"
        return "absent"
    before = len(robot.actions)
    error = await _call(
        hass,
        DOMAIN,
        "xiaomi_add_schedule",
        {
            "entity_id": entity_id,
            "enable": True,
            "day": 1,
            "hour": 8,
            "minute": 30,
            "repeat": False,
        },
    )
    if error is not None:
        return f"fail:{error}"
    if (8, 4) not in robot.actions[before:]:
        return "fail:schedule not sent"
    return "pass"


async def _room(
    hass: HomeAssistant,
    entry_id: str,
    entity_id: str,
    robot: SpecRobot,
    family: object,
) -> str:
    address = getattr(family, "room_sweep", None)
    if not isinstance(address, tuple):
        error = await _call(
            hass,
            DOMAIN,
            "vacuum_clean_segment",
            {"entity_id": entity_id, "segments": [1]},
        )
        if error is None:
            return "fail:room clean accepted"
        return "absent"
    before = len(robot.actions)
    error = await _call(
        hass,
        DOMAIN,
        "vacuum_clean_segment",
        {"entity_id": entity_id, "segments": [1]},
    )
    if error is not None:
        return f"fail:{error}"
    if (address[0], address[1]) not in robot.actions[before:]:
        return "fail:room action not sent"
    await _refresh(hass, entry_id)
    state = hass.states.get(entity_id)
    if state is None or state.state != "cleaning":
        actual = None if state is None else state.state
        return f"fail:state {actual}"
    return "pass"


async def _error(
    hass: HomeAssistant, entry_id: str, robot: SpecRobot, entity_id: str
) -> str:
    if robot.set_fault() is None:
        return "absent"
    robot.set_stored(StoredState.ERROR)
    await _refresh(hass, entry_id)
    state = hass.states.get(entity_id)
    if state is None or state.state != "error":
        actual = None if state is None else state.state
        return f"fail:state {actual}"
    return "pass"


def _write_matrix(matrix: dict[str, dict[str, str]]) -> None:
    if not _ARTIFACT.parent.is_dir():
        return
    _ARTIFACT.write_text(json.dumps(matrix, indent=2, sort_keys=True), encoding="utf-8")


def _action(family: object, name: str) -> tuple[int, int] | None:
    overrides = getattr(family, "action_overrides", None)
    if not isinstance(overrides, dict) or name not in overrides:
        return None
    mapping = overrides[name]
    siid = mapping.get("siid")
    aiid = mapping.get("aiid")
    if not isinstance(siid, int) or not isinstance(aiid, int):
        return None
    return siid, aiid


def _owned(hass: HomeAssistant, code: str) -> list[State]:
    needle = f"lab_{code}"
    return [
        state
        for state in hass.states.async_all()
        if state.entity_id == f"vacuum.{needle}" or f"{needle}_" in state.entity_id
    ]


def _named(states: list[State], domain: str, suffix: str) -> State | None:
    found = [
        state
        for state in states
        if state.domain == domain and state.entity_id.endswith(f"_{suffix}")
    ]
    if not found:
        return None
    return found[0]


async def _call(
    hass: HomeAssistant, domain: str, service: str, data: dict[str, object]
) -> str | None:
    try:
        await hass.services.async_call(domain, service, data, blocking=True)
    except HomeAssistantError as exc:
        return str(exc).splitlines()[0][:120]
    return None


async def _refresh(hass: HomeAssistant, entry_id: str) -> None:
    coordinator = hass.data[DOMAIN][entry_id]
    await hass.async_add_executor_job(coordinator.device._request_properties)
    coordinator.async_set_updated_data()
    await hass.async_block_till_done()

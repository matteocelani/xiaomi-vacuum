"""Drive every control of every canonical model through Home Assistant."""

from __future__ import annotations

from custom_components.xiaomi_robot_vacuum.const import (
    CONF_ACCOUNT_TYPE,
    CONF_MAC,
    CONF_NOTIFY,
    CONF_PREFER_CLOUD,
    CONF_VERSION,
    DOMAIN,
)
from custom_components.xiaomi_robot_vacuum.xiaomi.mapping import resolve_family
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry
from tests.virtual.dreame_map_robot import DreameMapRobot
from tests.virtual.fleet_catalog import robot_profiles
from tests.virtual.miio_endpoint import MiioEndpoint
from tests.virtual.spec_robot import SpecRobot
from tests.xiaomi.helpers import release_device

from homeassistant.const import CONF_HOST, CONF_MODEL, CONF_NAME, CONF_TOKEN
from homeassistant.core import HomeAssistant, State
from homeassistant.exceptions import HomeAssistantError

_TOKEN = "00" * 16

pytestmark = [
    pytest.mark.ha,
    pytest.mark.enable_socket,
    pytest.mark.allow_hosts(["127.0.0.1"]),
]


async def test_every_control_on_every_canonical_model(
    hass: HomeAssistant,
    socket_enabled: None,
    enable_custom_integrations: None,
    integration_package: object,
) -> None:
    """Each select, switch, number, and button reaches the robot."""
    del socket_enabled, enable_custom_integrations, integration_package
    from custom_components.xiaomi_robot_vacuum.dreame import VERSION

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
            entry = _entry(profile.model, code, mac, VERSION)
            entry.add_to_hass(hass)
            assert await hass.config_entries.async_setup(entry.entry_id)
            await hass.async_block_till_done()
            device = hass.data[DOMAIN][entry.entry_id].device
            try:
                failures.extend(
                    await _exercise(hass, entry.entry_id, profile.model, code)
                )
            finally:
                await hass.config_entries.async_unload(entry.entry_id)
                await hass.async_block_till_done()
                release_device(device)
    assert not failures, "\n".join(failures)


async def test_dreame_catalog_model_starts_and_docks(
    hass: HomeAssistant,
    socket_enabled: None,
    enable_custom_integrations: None,
    integration_package: object,
) -> None:
    """The Dreame sample accepts start and return-to-base without a crash."""
    del socket_enabled, enable_custom_integrations, integration_package
    from custom_components.xiaomi_robot_vacuum.dreame import VERSION
    from custom_components.xiaomi_robot_vacuum.dreame.catalog import (
        load_model_catalog,
    )
    from custom_components.xiaomi_robot_vacuum.dreame.const import DEVICE_INFO

    model = sorted(
        item for item in load_model_catalog(DEVICE_INFO) if item.startswith("dreame.")
    )[0]
    mac = "00:00:00:00:00:fe"
    robot = DreameMapRobot(model, mac)
    with MiioEndpoint(robot):
        entry = _entry(model, "dreame", mac, VERSION, name="Lab Dreame")
        entry.add_to_hass(hass)
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        device = hass.data[DOMAIN][entry.entry_id].device
        try:
            vacuum = _owned(hass, "dreame", vacuum_name="lab_dreame")
            assert vacuum is not None
            for service in ("start", "pause", "stop", "return_to_base"):
                error = await _call(
                    hass,
                    "vacuum",
                    service,
                    {"entity_id": vacuum.entity_id},
                )
                assert error is None, f"{model} {service} {error}"
        finally:
            await hass.config_entries.async_unload(entry.entry_id)
            await hass.async_block_till_done()
            release_device(device)


def _entry(
    model: str,
    code: str,
    mac: str,
    version: object,
    name: str | None = None,
) -> MockConfigEntry:
    return MockConfigEntry(
        domain=DOMAIN,
        unique_id=model,
        data={
            CONF_NAME: name or f"Lab {code}",
            CONF_HOST: "127.0.0.1",
            CONF_TOKEN: _TOKEN,
            CONF_MAC: mac,
            CONF_MODEL: model,
            CONF_ACCOUNT_TYPE: "mi",
        },
        options={
            CONF_PREFER_CLOUD: False,
            CONF_NOTIFY: False,
            CONF_VERSION: version,
        },
    )


async def _exercise(
    hass: HomeAssistant, entry_id: str, model: str, code: str
) -> list[str]:
    failures: list[str] = []
    states = _owned(hass, code)
    for state in states:
        if state.domain == "select":
            failures.extend(await _select(hass, entry_id, model, state))
        elif state.domain == "switch":
            failures.extend(await _switch(hass, entry_id, model, state))
        elif state.domain == "number":
            failures.extend(await _number(hass, entry_id, model, state))
        elif state.domain == "button":
            error = await _call(hass, "button", "press", {"entity_id": state.entity_id})
            if error is not None:
                failures.append(f"{model} button {state.entity_id} {error}")
    return failures


async def _select(
    hass: HomeAssistant, entry_id: str, model: str, state: State
) -> list[str]:
    if state.state in {"unknown", "unavailable"}:
        return [f"{model} select {state.entity_id} {state.state}"]
    options = state.attributes.get("options")
    if not isinstance(options, list) or len(options) < 2:
        return []
    option = next(item for item in options if item != state.state)
    error = await _call(
        hass,
        "select",
        "select_option",
        {"entity_id": state.entity_id, "option": option},
    )
    if error is not None:
        return [f"{model} select {state.entity_id} {error}"]
    await _refresh(hass, entry_id)
    updated = hass.states.get(state.entity_id)
    if updated is None or updated.state != option:
        actual = None if updated is None else updated.state
        return [f"{model} select {state.entity_id} now {actual}"]
    return []


async def _switch(
    hass: HomeAssistant, entry_id: str, model: str, state: State
) -> list[str]:
    if state.state not in {"on", "off"}:
        return [f"{model} switch {state.entity_id} {state.state}"]
    service = "turn_off" if state.state == "on" else "turn_on"
    expected = "off" if service == "turn_off" else "on"
    error = await _call(hass, "switch", service, {"entity_id": state.entity_id})
    if error is not None:
        return [f"{model} switch {state.entity_id} {error}"]
    await _refresh(hass, entry_id)
    updated = hass.states.get(state.entity_id)
    if updated is None or updated.state != expected:
        actual = None if updated is None else updated.state
        return [f"{model} switch {state.entity_id} now {actual}"]
    return []


async def _number(
    hass: HomeAssistant, entry_id: str, model: str, state: State
) -> list[str]:
    if state.state in {"unknown", "unavailable"}:
        return [f"{model} number {state.entity_id} {state.state}"]
    maximum = state.attributes.get("max")
    if not isinstance(maximum, (int, float)):
        return []
    error = await _call(
        hass,
        "number",
        "set_value",
        {"entity_id": state.entity_id, "value": maximum},
    )
    if error is not None:
        return [f"{model} number {state.entity_id} {error}"]
    await _refresh(hass, entry_id)
    updated = hass.states.get(state.entity_id)
    if updated is None or float(updated.state) != float(maximum):
        actual = None if updated is None else updated.state
        return [f"{model} number {state.entity_id} now {actual}"]
    return []


def _owned(
    hass: HomeAssistant, code: str, vacuum_name: str | None = None
) -> list[State] | State | None:
    needle = f"lab_{code}_"
    vacuum_id = f"vacuum.{vacuum_name or f'lab_{code}'}"
    found = [
        state
        for state in hass.states.async_all()
        if state.entity_id == vacuum_id or needle in state.entity_id
    ]
    if vacuum_name is not None:
        for state in found:
            if state.entity_id == vacuum_id:
                return state
        return None
    return found


async def _call(
    hass: HomeAssistant, domain: str, service: str, data: dict[str, object]
) -> str | None:
    try:
        await hass.services.async_call(domain, service, data, blocking=True)
    except HomeAssistantError as exc:
        return str(exc).splitlines()[0][:160]
    return None


async def _refresh(hass: HomeAssistant, entry_id: str) -> None:
    coordinator = hass.data[DOMAIN][entry_id]
    await hass.async_add_executor_job(coordinator.device._request_properties)
    coordinator.async_set_updated_data()
    await hass.async_block_till_done()

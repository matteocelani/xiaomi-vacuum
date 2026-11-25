"""Start a Home Assistant config loaded with one spec robot per model."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
import json
import logging
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time
import urllib.request
import uuid

_LOGGER = logging.getLogger("virtual_lab")
_ROOT = Path(__file__).resolve().parents[2]
# The script is executed as a file, so the repository root is not on sys.path yet.
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from custom_components.xiaomi_robot_vacuum.dreame import (  # noqa: E402
    DEVICE_INFO,
    VERSION,
)
from custom_components.xiaomi_robot_vacuum.dreame.catalog import (  # noqa: E402
    load_model_catalog,
)
from custom_components.xiaomi_robot_vacuum.dreame.map import (  # noqa: E402
    DreameVacuumMapDecoder,
    DreameVacuumMapRenderer,
)
from custom_components.xiaomi_robot_vacuum.xiaomi.mapping import (  # noqa: E402
    resolve_family,
)
from tests.virtual.dreame_map_robot import DreameMapRobot  # noqa: E402
from tests.virtual.fleet_catalog import (  # noqa: E402
    representative_models,
    robot_profiles,
)
from tests.virtual.floor_plan import encode_floor_plan  # noqa: E402
from tests.virtual.miio_endpoint import MiioEndpoint  # noqa: E402
from tests.virtual.spec_robot import SpecRobot  # noqa: E402

_TOKEN = "00" * 16
_PACKAGE = _ROOT / "custom_components" / "xiaomi_robot_vacuum"


@dataclass(frozen=True, slots=True)
class LabDevice:
    """One config entry and the address of its simulated robot."""

    name: str
    model: str
    host: str
    mac: str
    family: str


def main() -> None:
    """Bind every canonical model, write a Home Assistant config, and run it."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    config = Path(os.environ.get("VIRTUAL_LAB_CONFIG", _ROOT / ".virtual-lab"))
    devices = _devices()
    endpoints = _start(devices)
    try:
        _write_config(config, devices)
        _LOGGER.info("config %s", config)
        _LOGGER.info("models %s", len(devices))
        _run_home_assistant(config)
    finally:
        for endpoint in endpoints:
            endpoint.close()


def _devices() -> tuple[LabDevice, ...]:
    devices: list[LabDevice] = []
    families = {model: name for name, model in representative_models()}
    index = 1
    for profile in robot_profiles():
        if profile.submodel:
            continue
        code = profile.model.rsplit(".", 1)[-1]
        devices.append(
            LabDevice(
                name=f"Lab {code}",
                model=profile.model,
                host=f"127.0.0.{index}",
                mac=f"00:00:00:00:00:{index:02x}",
                family=families.get(profile.model, "xiaomi"),
            )
        )
        index += 1
    dreame = _dreame_model()
    devices.append(
        LabDevice(
            name="Lab Dreame",
            model=dreame,
            host="127.0.0.254",
            mac="00:00:00:00:00:fe",
            family="dreame",
        )
    )
    return tuple(devices)


def _dreame_model() -> str:
    catalog = load_model_catalog(DEVICE_INFO)
    found = sorted(model for model in catalog if model.startswith("dreame."))
    if not found:
        raise RuntimeError("catalog has no Dreame model")
    return found[0]


def _start(devices: Sequence[LabDevice]) -> list[MiioEndpoint]:
    endpoints: list[MiioEndpoint] = []
    for device in devices:
        if device.family == "dreame":
            robot = DreameMapRobot(device.model, device.mac)
        else:
            profile = _profile(device.model)
            family = resolve_family(device.model)
            if family is None:
                raise RuntimeError(device.model)
            robot = SpecRobot(device.model, profile, mac=device.mac)
            robot.apply_family(family)
        endpoint = MiioEndpoint(robot, host=device.host)
        endpoint.start()
        endpoints.append(endpoint)
        _LOGGER.info("robot %s %s %s", device.model, device.host, device.family)
    return endpoints


def _profile(model: str) -> dict[str, object]:
    for profile in robot_profiles():
        if profile.model == model and not profile.submodel:
            return profile.document()
    raise KeyError(model)


def _write_config(config: Path, devices: Sequence[LabDevice]) -> None:
    if config.exists():
        shutil.rmtree(config)
    config.mkdir(parents=True)
    component = config / "custom_components" / "xiaomi_robot_vacuum"
    component.parent.mkdir(parents=True)
    component.symlink_to(_PACKAGE, target_is_directory=True)
    www = config / "www" / "maps"
    www.mkdir(parents=True)
    _render_maps(www, devices)
    (config / "configuration.yaml").write_text(_configuration(), encoding="utf-8")
    (config / "ui-lovelace.yaml").write_text(_dashboard(devices), encoding="utf-8")
    storage = config / ".storage"
    storage.mkdir()
    (storage / "core.config_entries").write_text(
        json.dumps(_entries(devices), indent=2),
        encoding="utf-8",
    )
    (storage / "core.onboarding").write_text(
        json.dumps(
            {
                "version": 1,
                "minor_version": 1,
                "key": "core.onboarding",
                "data": {"done": ["user", "core_config", "analytics", "integration"]},
            }
        ),
        encoding="utf-8",
    )
    (config / "lab-devices.json").write_text(
        json.dumps(
            [
                {
                    "name": device.name,
                    "model": device.model,
                    "host": device.host,
                    "family": device.family,
                    "entity_id": f"vacuum.{_slug(device.name)}",
                }
                for device in devices
            ],
            indent=2,
        ),
        encoding="utf-8",
    )


def _render_maps(www: Path, devices: Sequence[LabDevice]) -> None:
    decoded = DreameVacuumMapDecoder.decode_map(encode_floor_plan())
    image = DreameVacuumMapRenderer().render_map(decoded[0])
    seen: set[str] = set()
    for device in devices:
        if device.family not in {
            "station",
            "sweep",
            "essential",
            "robot",
            "roller",
            "mijia-cn",
            "dreame",
        }:
            continue
        if device.family in seen:
            continue
        seen.add(device.family)
        (www / f"{device.family}.png").write_bytes(image)


def _configuration() -> str:
    return (
        "default_config:\n"
        "homeassistant:\n"
        "  name: Virtual vacuum lab\n"
        "  unit_system: metric\n"
        "  time_zone: UTC\n"
        "lovelace:\n"
        "  mode: yaml\n"
        "http:\n"
        "  server_port: 8123\n"
        "logger:\n"
        "  default: warning\n"
        "  logs:\n"
        "    custom_components.xiaomi_robot_vacuum: info\n"
    )


def _dashboard(devices: Sequence[LabDevice]) -> str:
    lines = [
        "title: Virtual vacuum lab",
        "views:",
        "  - title: Lab",
        "    path: lab",
        "    cards:",
    ]
    for device in devices:
        if device.family == "xiaomi":
            continue
        lines.extend(
            [
                "      - type: tile",
                f"        entity: vacuum.{_slug(device.name)}",
                "        features:",
                "          - type: vacuum-commands",
                "            commands:",
                "              - start_pause",
                "              - stop",
                "              - return_home",
                "      - type: picture",
                f"        image: /local/maps/{device.family}.png",
                f"        alt_text: {device.family} map",
            ]
        )
    lines.extend(
        [
            "      - type: entities",
            "        title: All virtual robots",
            "        entities:",
        ]
    )
    for device in devices:
        lines.append(f"          - vacuum.{_slug(device.name)}")
    return "\n".join(lines) + "\n"


def _entries(devices: Sequence[LabDevice]) -> dict[str, object]:
    now = "2026-11-25T09:00:00+00:00"
    entries = []
    for device in devices:
        entries.append(
            {
                "created_at": now,
                "modified_at": now,
                "entry_id": uuid.uuid4().hex,
                "domain": "xiaomi_robot_vacuum",
                "title": device.name,
                "source": "user",
                "unique_id": device.mac,
                "version": 2,
                "minor_version": 1,
                "data": {
                    "name": device.name,
                    "host": device.host,
                    "token": _TOKEN,
                    "mac": device.mac,
                    "model": device.model,
                    "account_type": "mi",
                },
                "options": {
                    "prefer_cloud": False,
                    "notify": False,
                    "version": VERSION,
                },
                "pref_disable_new_entities": False,
                "pref_disable_polling": False,
                "disabled_by": None,
                "discovery_keys": {},
            }
        )
    return {
        "version": 1,
        "minor_version": 4,
        "key": "core.config_entries",
        "data": {"entries": entries},
    }


def _slug(name: str) -> str:
    return name.lower().replace(" ", "_")


def _run_home_assistant(config: Path) -> None:
    command = [sys.executable, "-m", "homeassistant", "--config", str(config)]
    _LOGGER.info("starting %s", " ".join(command))
    process = subprocess.Popen(command)
    try:
        _wait_until_up()
        _LOGGER.info("open http://127.0.0.1:8123/lovelace/lab")
        while process.poll() is None:
            time.sleep(1)
    finally:
        if process.poll() is None:
            process.send_signal(signal.SIGTERM)
            try:
                process.wait(timeout=20)
            except subprocess.TimeoutExpired:
                process.kill()


def _wait_until_up() -> None:
    deadline = time.monotonic() + 180
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(
                "http://127.0.0.1:8123/", timeout=2
            ) as response:
                if response.status < 500:
                    return
        except OSError:
            time.sleep(1)
    raise RuntimeError("Home Assistant did not open port 8123")


if __name__ == "__main__":
    main()

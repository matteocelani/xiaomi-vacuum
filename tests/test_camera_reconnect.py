"""A cloud reconnect does not render every map camera immediately."""

from __future__ import annotations

import importlib
from pathlib import Path
import sys
from types import SimpleNamespace


def _load_camera():
    dreame_name = "custom_components.dreame_vacuum.dreame"
    dreame = sys.modules.get(dreame_name)
    if dreame is not None and not hasattr(dreame, "VERSION"):
        init = (
            Path(__file__).resolve().parents[1]
            / "custom_components"
            / "dreame_vacuum"
            / "dreame"
            / "__init__.py"
        )
        executed = compile(init.read_text(encoding="utf-8"), str(init), "exec")
        exec(executed, dreame.__dict__)
    package = "custom_components.dreame_vacuum"
    module = sys.modules.get(package)
    if module is None or not hasattr(module, "async_setup_entry"):
        sys.modules.pop(package, None)
        importlib.import_module(package)
    return importlib.import_module("custom_components.dreame_vacuum.camera")


def test_update_after_reconnect_waits_for_an_image_request() -> None:
    camera = _load_camera()
    entity = object.__new__(camera.DreameVacuumCameraEntity)
    map_data = SimpleNamespace(last_updated=10, timestamp_ms=None, frame_id=1)
    device = SimpleNamespace(
        cloud_connected=True,
        status=SimpleNamespace(located=True, active=True),
        get_map=lambda _index: map_data,
    )
    object.__setattr__(entity, "coordinator", SimpleNamespace(device=device))
    object.__setattr__(entity, "entity_description", SimpleNamespace(map_type="current"))
    entity.map_index = 0
    entity._default_map = True
    entity._last_rendered = None
    entity._last_updated = None
    entity._frame_id = None
    entity._state = None
    entity._renderer = None
    entity._proxy_renderer = None

    entity.update()

    assert entity._default_map is True
    assert entity._last_updated == 10
    assert entity._frame_id == 1

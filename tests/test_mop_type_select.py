"""A room with no mop type does not break the per-room select."""

from __future__ import annotations

import importlib
from pathlib import Path
import sys
from types import SimpleNamespace


def _load_select():
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
    return importlib.import_module("custom_components.dreame_vacuum.select")


def _device() -> SimpleNamespace:
    return SimpleNamespace(
        status=SimpleNamespace(
            current_segments=True,
            started=False,
            cruising=False,
            has_saved_map=True,
            fast_mapping=False,
            auto_change_mop=True,
        )
    )


def test_missing_mop_type_makes_the_room_select_unavailable() -> None:
    select = _load_select()
    description = next(
        item for item in select.SEGMENT_SELECTS if item.key == "mop_type"
    )
    device = _device()

    assert not description.segment_available_fn(device, None)
    assert not description.segment_available_fn(device, SimpleNamespace(mop_type=None))
    assert description.segment_available_fn(device, SimpleNamespace(mop_type="A"))
    assert description.value_int_fn("a", None) == "A"

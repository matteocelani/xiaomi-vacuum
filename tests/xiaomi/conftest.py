"""Shared Home Assistant loader for Xiaomi loopback tests."""

from __future__ import annotations

import importlib
from pathlib import Path
import sys

import pytest

pytest.register_assert_rewrite(
    "tests.xiaomi.entity_contract",
    "tests.xiaomi.spec_helpers",
)


@pytest.fixture
def integration_package() -> object:
    """Load the real integration package over the device-core import stub."""
    dreame_name = "custom_components.xiaomi_robot_vacuum.dreame"
    dreame = sys.modules.get(dreame_name)
    if dreame is not None and not hasattr(dreame, "VERSION"):
        init = (
            Path(__file__).resolve().parents[2]
            / "custom_components"
            / "xiaomi_robot_vacuum"
            / "dreame"
            / "__init__.py"
        )
        executed = compile(init.read_text(encoding="utf-8"), str(init), "exec")
        exec(executed, dreame.__dict__)
    package = "custom_components.xiaomi_robot_vacuum"
    module = sys.modules.get(package)
    if module is None or not hasattr(module, "async_setup_entry"):
        sys.modules.pop(package, None)
        module = importlib.import_module(package)
    return module

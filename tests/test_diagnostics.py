"""Diagnostics redaction for values that must not leave the house."""

from __future__ import annotations

import importlib
from pathlib import Path
import sys


def _load_diagnostics():
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
    return importlib.import_module("custom_components.dreame_vacuum.diagnostics")


def test_matter_pairing_code_is_redacted() -> None:
    diagnostics = _load_diagnostics()
    payload = {
        "MATTER_QR_CODE": "MT:FAKE-PAIRING-CODE",
        "matter_qr_code": "MT:FAKE-PAIRING-CODE",
        "nested": {"matter_qr_code": "MT:ALSO-FAKE", "battery": 80},
    }

    sanitized = diagnostics._sanitize(payload)

    assert "MATTER_QR_CODE" not in sanitized
    assert "matter_qr_code" not in sanitized
    assert "matter_qr_code" not in sanitized["nested"]
    assert sanitized["nested"]["battery"] == 80

"""Reset a consumable through the sweep-family button when the model publishes one."""

from __future__ import annotations

from typing import Final

from .controls import XiaomiControl, invoke_control

_RESET_KEYS: Final = {
    "main_brush": "xiaomi_reset_main_brush",
    "side_brush": "xiaomi_reset_side_brush",
    "filter": "xiaomi_reset_filter",
    "mop_pad": "xiaomi_reset_mop",
}


def reset_published_consumable(device: object, consumable: str) -> bool:
    """Call the sweep reset button. False means this model has no such button."""
    key = _RESET_KEYS.get(consumable)
    if key is None:
        return False
    control = _control(device, key)
    if control is None:
        return False
    invoke_control(device, control)
    return True


def _control(device: object, key: str) -> XiaomiControl | None:
    codec = getattr(device, "_property_codec", None)
    controls = getattr(codec, "controls", None)
    if not isinstance(controls, tuple):
        return None
    for control in controls:
        if isinstance(control, XiaomiControl) and control.key == key:
            return control
    return None

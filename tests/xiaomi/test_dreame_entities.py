"""Dreame entity descriptions stay available on the Dreame action map."""

from __future__ import annotations

from types import SimpleNamespace

from custom_components.dreame_vacuum.dreame.types import (
    DreameVacuumActionMapping,
    DreameVacuumProperty,
    DreameVacuumPropertyMapping,
)
import pytest


def test_dreame_button_actions_stay_on_the_dreame_map(
    integration_package: object,
) -> None:
    del integration_package
    pytest.importorskip("homeassistant")
    from custom_components.dreame_vacuum.button import BUTTONS
    from custom_components.dreame_vacuum.entity import description_exists

    device = SimpleNamespace(
        action_mapping=DreameVacuumActionMapping,
        property_mapping=DreameVacuumPropertyMapping,
        data={item.value: 0 for item in DreameVacuumProperty},
        auto_switch_data={},
        ai_data={},
    )
    action_keys = [item.action_key for item in BUTTONS if item.action_key is not None]
    assert action_keys
    assert set(action_keys) <= set(DreameVacuumActionMapping)
    for description in BUTTONS:
        if description.action_key is None or description.property_key is not None:
            continue
        assert description_exists(description, device)

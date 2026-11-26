"""Service descriptions must offer the values the handler accepts."""

from __future__ import annotations

from pathlib import Path

from custom_components.xiaomi_robot_vacuum.const import (
    CONSUMABLE_DEODORIZER,
    CONSUMABLE_DETERGENT,
    CONSUMABLE_DIRTY_WATER_CHANNEL,
    CONSUMABLE_FILTER,
    CONSUMABLE_FLUFFING_ROLLER,
    CONSUMABLE_MAIN_BRUSH,
    CONSUMABLE_MOP_PAD,
    CONSUMABLE_ONBOARD_DIRTY_WATER_TANK,
    CONSUMABLE_ROLLER_MOP_FILTER,
    CONSUMABLE_SCALE_INHIBITOR,
    CONSUMABLE_SENSOR,
    CONSUMABLE_SIDE_BRUSH,
    CONSUMABLE_SILVER_ION,
    CONSUMABLE_SQUEEGEE,
    CONSUMABLE_TANK_FILTER,
    CONSUMABLE_WATER_OUTLET_FILTER,
    CONSUMABLE_WHEEL,
)
import yaml

_ACCEPTED = [
    CONSUMABLE_MAIN_BRUSH,
    CONSUMABLE_SIDE_BRUSH,
    CONSUMABLE_FILTER,
    CONSUMABLE_TANK_FILTER,
    CONSUMABLE_SENSOR,
    CONSUMABLE_MOP_PAD,
    CONSUMABLE_SILVER_ION,
    CONSUMABLE_DETERGENT,
    CONSUMABLE_SQUEEGEE,
    CONSUMABLE_ONBOARD_DIRTY_WATER_TANK,
    CONSUMABLE_DIRTY_WATER_CHANNEL,
    CONSUMABLE_DEODORIZER,
    CONSUMABLE_WHEEL,
    CONSUMABLE_SCALE_INHIBITOR,
    CONSUMABLE_FLUFFING_ROLLER,
    CONSUMABLE_ROLLER_MOP_FILTER,
    CONSUMABLE_WATER_OUTLET_FILTER,
]


def test_reset_consumable_options_match_the_handler() -> None:
    """The service menu must list dirty_water_channel, which is what reset accepts."""
    document = yaml.safe_load(
        Path("custom_components/xiaomi_robot_vacuum/services.yaml").read_text(
            encoding="utf-8"
        )
    )
    options = document["vacuum_reset_consumable"]["fields"]["consumable"]["selector"][
        "select"
    ]["options"]

    assert options == _ACCEPTED

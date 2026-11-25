"""The generated floor plan decodes and renders through the Dreame map pipeline."""

from __future__ import annotations

from custom_components.xiaomi_robot_vacuum.dreame.map import (
    DreameVacuumMapDecoder,
    DreameVacuumMapRenderer,
)
from tests.virtual.dreame_map_robot import DreameMapRobot
from tests.virtual.floor_plan import FLOOR_HEIGHT, FLOOR_WIDTH, encode_floor_plan


def test_floor_plan_decodes_two_rooms_and_renders_a_png() -> None:
    """Kitchen and Hall survive decode, and the renderer returns a PNG."""
    decoded = DreameVacuumMapDecoder.decode_map(encode_floor_plan())
    current = decoded[0]
    assert current is not None
    assert current.dimensions.width == FLOOR_WIDTH
    assert current.dimensions.height == FLOOR_HEIGHT
    assert 1 in current.segments
    assert 2 in current.segments
    assert current.segments[1].custom_name == "Kitchen"
    assert current.segments[2].custom_name == "Hall"
    image = DreameVacuumMapRenderer().render_map(current)
    assert image.startswith(b"\x89PNG")
    assert len(image) > 1000


def test_dreame_request_map_returns_the_same_floor_plan() -> None:
    """The Dreame family robot answers REQUEST_MAP with that frame."""
    robot = DreameMapRobot("dreame.vacuum.lab")
    result = robot.dispatch(
        "action",
        {"siid": 6, "aiid": 1, "in": []},
    )
    assert isinstance(result, dict)
    assert result["code"] == 0
    values = [item["value"] for item in result["out"] if item["piid"] == 1]
    assert values == [robot.floor_plan]
    info = robot.dispatch("miIO.info", [])
    assert isinstance(info, dict)
    assert info["model"] == "dreame.vacuum.lab"

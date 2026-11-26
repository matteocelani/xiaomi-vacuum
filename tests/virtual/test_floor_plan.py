"""The generated floor plan decodes and renders through the Dreame map pipeline."""

from __future__ import annotations

from io import BytesIO

from custom_components.xiaomi_robot_vacuum.dreame.map import (
    DreameVacuumMapDecoder,
    DreameVacuumMapRenderer,
)
from PIL import Image
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
    _assert_rooms_fill_the_frame(image)


def _assert_rooms_fill_the_frame(image: bytes) -> None:
    """The two rooms must occupy the frame, not sit as a speck in the padding."""
    rendered = Image.open(BytesIO(image)).convert("RGBA")
    width, height = rendered.size
    corner = rendered.getpixel((0, 0))
    counts: dict[tuple[int, int, int, int], int] = {}
    for pixel in rendered.getdata():
        if pixel == corner:
            continue
        counts[pixel] = counts.get(pixel, 0) + 1
    covered = sum(counts.values())
    assert covered / (width * height) >= 0.45
    assert sum(1 for count in counts.values() if count / (width * height) >= 0.1) >= 2


def test_docked_dreame_robot_does_not_publish_an_idle_status() -> None:
    """A charging dock must not report status 0, which the card shows as Idle."""
    robot = DreameMapRobot("dreame.vacuum.lab")

    def read(siid: int, piid: int) -> object:
        result = robot.dispatch(
            "get_properties",
            [{"did": "s", "siid": siid, "piid": piid}],
        )
        assert isinstance(result, list)
        item = result[0]
        assert isinstance(item, dict)
        return item["value"]

    battery = read(3, 1)
    assert isinstance(battery, int)
    assert read(2, 1) == 6
    assert read(4, 1) == 6
    assert read(3, 2) == 1
    charge_level = read(28, 47)
    assert isinstance(charge_level, int)
    assert charge_level > battery


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

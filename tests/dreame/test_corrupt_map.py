"""A bad map field must not drop rooms or crash the decoder."""

from __future__ import annotations

import base64
import json
import struct
import zlib

from custom_components.xiaomi_robot_vacuum.dreame.map import (
    DreameVacuumMapDecoder,
    DreameVacuumMapRenderer,
)
from custom_components.xiaomi_robot_vacuum.dreame.types import MapData
from custom_components.xiaomi_robot_vacuum.xiaomi import resolve_family
from tests.virtual.floor_plan import FLOOR_HEIGHT, FLOOR_WIDTH, encode_floor_plan
from tests.xiaomi.deep.corpus import manifest_models

_HEADER_SIZE = 27
_GRID_BYTES = FLOOR_WIDTH * FLOOR_HEIGHT
_MAP_MODELS = (
    "mijia.vacuum.b108za",
    "mijia.vacuum.b108zb",
    "mijia.vacuum.b108zh",
    "xiaomi.vacuum.b108gl",
)


def _frame(extra: dict[str, object] | None = None, map_id: int | None = None) -> str:
    """Return the lab floor with optional JSON fields and a chosen map id."""
    raw = zlib.decompress(base64.b64decode(encode_floor_plan()))
    header = bytearray(raw[:_HEADER_SIZE])
    if map_id is not None:
        struct.pack_into("<H", header, 0, map_id)
    payload = json.loads(raw[_HEADER_SIZE + _GRID_BYTES :])
    if extra:
        payload.update(extra)
    body = bytes(header) + raw[_HEADER_SIZE : _HEADER_SIZE + _GRID_BYTES]
    body += json.dumps(payload).encode("utf-8")
    return base64.b64encode(zlib.compress(body)).decode("ascii")


def _current(frame: str) -> MapData:
    decoded = DreameVacuumMapDecoder.decode_map(frame)
    assert isinstance(decoded, tuple)
    current = decoded[0]
    assert isinstance(current, MapData)
    return current


def _assert_rooms(current: MapData) -> None:
    assert current.dimensions.width == FLOOR_WIDTH
    assert current.dimensions.height == FLOOR_HEIGHT
    assert current.pixel_type is not None
    assert 1 in current.segments
    assert 2 in current.segments
    assert current.segments[1].custom_name == "Kitchen"
    assert current.segments[2].custom_name == "Hall"


def test_bad_rotation_keeps_rooms_and_zones() -> None:
    """A non-numeric rotation must not discard the rooms or the no-go zone."""
    current = _current(
        _frame(
            {
                "mra": "nope",
                "vw": {
                    "rect": [[100, 100, 400, 400]],
                    "line": [[10, 20, 30, 40]],
                },
            }
        )
    )

    _assert_rooms(current)
    assert current.rotation == 0
    assert current.no_go_areas
    assert current.virtual_walls
    image = DreameVacuumMapRenderer().render_map(current)
    assert image.startswith(b"\x89PNG")
    assert len(image) > 1000


def test_bad_cleaning_time_keeps_rooms() -> None:
    """A non-numeric cleaning time must not discard the floor."""
    current = _current(_frame({"ct": "nope"}))

    _assert_rooms(current)
    image = DreameVacuumMapRenderer().render_map(current)
    assert image.startswith(b"\x89PNG")


def test_a_short_no_go_keeps_the_valid_zone() -> None:
    """One truncated rectangle must not drop the next no-go zone."""
    current = _current(
        _frame(
            {
                "vw": {
                    "rect": [[1, 2], [100, 100, 400, 400]],
                    "line": [[1], [5, 6, 7, 8]],
                }
            }
        )
    )

    _assert_rooms(current)
    assert len(current.no_go_areas) == 1
    assert len(current.virtual_walls) == 1


def test_a_short_carpet_keeps_later_walls() -> None:
    """One truncated carpet must not drop walls parsed after it."""
    current = _current(
        _frame(
            {
                "vw": {"addcpt": [[1, 2]]},
                "walls_info": {
                    "storeys": [
                        {
                            "rooms": [
                                {
                                    "room_id": 1,
                                    "walls": [[1, 0, 0, 10, 0, 0, 0, 0, 0, 10, 0]],
                                }
                            ]
                        }
                    ]
                },
            }
        )
    )

    _assert_rooms(current)
    assert current.walls
    assert 1 in current.walls


def test_rotated_floors_keep_their_angle() -> None:
    """Published rotation values stay on the decoded map and still render."""
    for angle in (0, 90, 180, 270):
        current = _current(_frame({"mra": angle}))
        _assert_rooms(current)
        assert current.rotation == angle
        image = DreameVacuumMapRenderer().render_map(current)
        assert image.startswith(b"\x89PNG")


def test_two_map_ids_stay_distinct() -> None:
    """Two floors do not collapse onto the same map id."""
    first = _current(_frame(map_id=1))
    second = _current(_frame(map_id=2))
    assert first.map_id == 1
    assert second.map_id == 2
    _assert_rooms(first)
    _assert_rooms(second)


def test_empty_and_corrupt_payloads_do_not_raise() -> None:
    """Missing, empty, and undecodable frames return no map."""
    for raw in (None, "", "%%%", "abc"):
        assert DreameVacuumMapDecoder.decode_map(raw) is None
        assert DreameVacuumMapDecoder.decode_saved_map(raw) is None

    header = bytearray(_HEADER_SIZE)
    struct.pack_into("<HHB", header, 0, 1, 1, 73)
    struct.pack_into("<HHHHH", header, 17, 50, 0, 0, 0, 0)
    empty = base64.b64encode(zlib.compress(bytes(header) + b"{}")).decode("ascii")
    current = _current(empty)
    assert current.dimensions.width == 0
    assert current.dimensions.height == 0
    image = DreameVacuumMapRenderer().render_map(current)
    assert isinstance(image, bytes)


def test_every_published_map_model_decodes_the_floor() -> None:
    """Each model that publishes a map frame decodes rooms, zones, and rotation."""
    frame = _frame(
        {
            "mra": 90,
            "vw": {"rect": [[100, 100, 400, 400]], "line": [[10, 20, 30, 40]]},
        }
    )
    found: list[str] = []
    for model in manifest_models():
        family = resolve_family(model)
        assert family is not None
        if family.map_address is None:
            continue
        found.append(model)
        assert family.map_address == (7, 5)
        current = _current(frame)
        _assert_rooms(current)
        assert current.rotation == 90
        assert current.no_go_areas
        assert current.virtual_walls
    assert found == list(_MAP_MODELS)


def test_fields_parsed_before_the_grid_do_not_drop_rooms() -> None:
    """A bad zone, point, cleanset, or room order must not discard the floor."""
    short_zone = _current(_frame({"da2": {"areas": [[1, 2], [10, 20, 30, 40]]}}))
    _assert_rooms(short_zone)
    assert len(short_zone.active_areas) == 1

    short_point = _current(_frame({"sp": [[1], [5, 6]]}))
    _assert_rooms(short_point)
    assert len(short_point.active_points) == 1

    bad_cleanset = _current(_frame({"cleanset": "not-json"}))
    _assert_rooms(bad_cleanset)
    assert bad_cleanset.cleanset is None

    bad_carpet = _current(_frame({"carpetcleanset": "not-json"}))
    _assert_rooms(bad_carpet)
    assert bad_carpet.carpet_cleanset is None

    bad_order = _current(_frame({"cleanareaorder": [{"nope": 1}, {"2": 3}]}))
    _assert_rooms(bad_order)
    assert bad_order.cleaning_sequence == {"2": 3}

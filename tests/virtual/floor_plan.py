"""Synthetic floor plan in the Dreame map frame the decoder already accepts."""

from __future__ import annotations

import base64
import json
import struct
from typing import Final
import zlib

# The renderer pads a map up to 120 by 80 cells. A smaller plan becomes a speck.
FLOOR_WIDTH: Final = 160
FLOOR_HEIGHT: Final = 110
_HEADER_SIZE: Final = 27
_FRAME_I: Final = 73
_GRID_MM: Final = 50
_KITCHEN: Final = 1
_HALL: Final = 2
_WALL: Final = 0x80
_SPLIT: Final = 80
_ROBOT_CELL: Final = (40, 55)
_CHARGER_CELL: Final = (12, 12)
_MAP_ID: Final = 1
_FRAME_ID: Final = 1


def encode_floor_plan(*, current: bool = False) -> str:
    """Return a base64 zlib I-frame with two rooms, a wall, and a dock.
    A current frame uses ris 0 and curtain, the map-v2 marks that keep room ids.
    """
    grid = bytearray(FLOOR_WIDTH * FLOOR_HEIGHT)
    for y in range(1, FLOOR_HEIGHT - 1):
        for x in range(1, _SPLIT):
            grid[(y * FLOOR_WIDTH) + x] = _KITCHEN
        grid[(y * FLOOR_WIDTH) + _SPLIT] = _WALL
        for x in range(_SPLIT + 1, FLOOR_WIDTH - 1):
            grid[(y * FLOOR_WIDTH) + x] = _HALL
    header = bytearray(_HEADER_SIZE)
    struct.pack_into("<HHB", header, 0, _MAP_ID, _FRAME_ID, _FRAME_I)
    struct.pack_into(
        "<hhh",
        header,
        5,
        _ROBOT_CELL[0] * _GRID_MM,
        _ROBOT_CELL[1] * _GRID_MM,
        0,
    )
    struct.pack_into(
        "<hhh",
        header,
        11,
        _CHARGER_CELL[0] * _GRID_MM,
        _CHARGER_CELL[1] * _GRID_MM,
        0,
    )
    struct.pack_into("<HHHHH", header, 17, _GRID_MM, FLOOR_WIDTH, FLOOR_HEIGHT, 0, 0)
    extra: dict[str, object] = {
        "timestamp_ms": 1_700_000_000_000,
        "seg_inf": {
            "1": {
                "type": 12,
                "index": 0,
                "name": base64.b64encode(b"Kitchen").decode("ascii"),
            },
            "2": {
                "type": 1,
                "index": 1,
                "name": base64.b64encode(b"Hall").decode("ascii"),
            },
        },
    }
    if current:
        extra["ris"] = 0
        extra["curtain"] = []
    raw = bytes(header) + bytes(grid) + json.dumps(extra).encode("utf-8")
    return base64.b64encode(zlib.compress(raw)).decode("ascii")


def room_summary() -> str:
    """Return the room list published on string map properties."""
    return json.dumps(
        {
            "rooms": [
                {"id": _KITCHEN, "name": "Kitchen"},
                {"id": _HALL, "name": "Hall"},
            ],
            "segments": [_KITCHEN, _HALL],
            "robot": {"x": 6, "y": 6},
            "charger": {"x": 2, "y": 2},
        },
        separators=(",", ":"),
    )

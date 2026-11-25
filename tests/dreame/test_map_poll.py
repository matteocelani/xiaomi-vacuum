"""An unchanged map frame must not be decoded on every poll."""

from __future__ import annotations

from types import SimpleNamespace

from custom_components.xiaomi_robot_vacuum.dreame.family_codec import (
    _load_published_map,
)
from custom_components.xiaomi_robot_vacuum.dreame.map import DreameVacuumMapDecoder


def test_the_same_map_frame_is_decoded_once(monkeypatch) -> None:
    """Forty-nine robots must not decode a map that has not changed."""
    decoded: list[str] = []

    def fake_decode(value: str):
        decoded.append(value)
        return (SimpleNamespace(last_updated=None), None)

    monkeypatch.setattr(DreameVacuumMapDecoder, "decode_map", staticmethod(fake_decode))

    class _Protocol:
        def get_properties(self, _items: object) -> list[dict[str, object]]:
            return [{"code": 0, "value": "frame"}]

    device = SimpleNamespace(_protocol=_Protocol(), status=SimpleNamespace())
    family = SimpleNamespace(map_address=(6, 1))

    assert _load_published_map(device, family) is True
    assert _load_published_map(device, family) is False
    assert decoded == ["frame"]

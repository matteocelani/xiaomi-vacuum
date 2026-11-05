"""Shared map-font cache stays small across renderers."""

from __future__ import annotations

from custom_components.dreame_vacuum.dreame.map import DreameVacuumMapRenderer


def test_loaded_fonts_are_shared_and_the_cache_stays_bounded() -> None:
    renderer = DreameVacuumMapRenderer
    renderer._font_cache.clear()
    renderer._font_files.clear()
    try:
        first = renderer._get_font(False, 12)
        assert renderer._get_font(False, 12) is first
        for size in range(13, 13 + renderer.FONT_CACHE_SIZE):
            renderer._get_font(False, size)
        assert len(renderer._font_cache) == renderer.FONT_CACHE_SIZE
        assert (False, 12) not in renderer._font_cache
    finally:
        renderer._font_cache.clear()
        renderer._font_files.clear()

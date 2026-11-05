"""Map object layers keep only the pixels that were drawn."""

from __future__ import annotations

from custom_components.dreame_vacuum.dreame.map import DreameVacuumMapRenderer
from PIL import Image


def test_crop_layer_keeps_the_drawn_box_and_its_position() -> None:
    image = Image.new("RGBA", (20, 10), (0, 0, 0, 0))
    image.putpixel((5, 3), (1, 2, 3, 255))
    image.putpixel((7, 4), (4, 5, 6, 255))

    cropped = DreameVacuumMapRenderer._crop_layer(image)

    assert cropped is not None
    layer, position = cropped
    assert position == (5, 3)
    assert layer is not None
    assert layer.size == (3, 2)
    assert layer.getpixel((0, 0)) == (1, 2, 3, 255)


def test_crop_layer_marks_an_empty_image_without_dropping_the_cache_entry() -> None:
    image = Image.new("RGBA", (4, 4), (0, 0, 0, 0))

    assert DreameVacuumMapRenderer._crop_layer(None) is None
    assert DreameVacuumMapRenderer._crop_layer(image) == (None, (0, 0))

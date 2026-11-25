"""Xiaomi models that publish a map frame expose it to the renderer."""

from __future__ import annotations

from io import BytesIO

from custom_components.xiaomi_robot_vacuum.dreame.device import DreameVacuumDevice
from custom_components.xiaomi_robot_vacuum.dreame.map import DreameVacuumMapRenderer
from custom_components.xiaomi_robot_vacuum.xiaomi.mapping import resolve_family
from PIL import Image
import pytest
from tests.virtual.fleet_catalog import robot_profiles
from tests.virtual.miio_endpoint import MiioEndpoint
from tests.virtual.spec_robot import SpecRobot
from tests.xiaomi.helpers import release_device

_TOKEN = "00" * 16
_MAC = "00:00:00:00:00:00"

pytestmark = [
    pytest.mark.enable_socket,
    pytest.mark.allow_hosts(["127.0.0.1"]),
]


def test_s20_plus_publishes_a_renderable_map(socket_enabled: None) -> None:
    """The permanent-map property becomes the camera's current map."""
    del socket_enabled
    profile = next(
        item
        for item in robot_profiles()
        if item.model == "xiaomi.vacuum.b108gl" and not item.submodel
    )
    family = resolve_family(profile.model)
    assert family is not None
    assert family.map_address == (7, 5)
    robot = SpecRobot(profile.model, profile.document(), mac=_MAC)
    robot.apply_family(family)
    with MiioEndpoint(robot):
        device = DreameVacuumDevice(
            "Lab",
            "127.0.0.1",
            _TOKEN,
            _MAC,
            account_type="mi",
            family_resolver=resolve_family,
            configured_model=profile.model,
        )
        device.connect_device()
        try:
            current = device.get_map(0)
            assert current is not None
            assert 1 in current.segments
            assert 2 in current.segments
            image = DreameVacuumMapRenderer().render_map(
                device.get_map_for_render(current)
            )
            assert image.startswith(b"\x89PNG")
            device._request_properties()
            assert device.get_map(0) is current
        finally:
            release_device(device)


def test_every_published_map_fills_the_camera_frame(socket_enabled: None) -> None:
    """Each model with a permanent map renders both rooms across the image."""
    del socket_enabled
    models = [
        profile.model
        for profile in robot_profiles()
        if not profile.submodel
        and isinstance(
            getattr(resolve_family(profile.model), "map_address", None), tuple
        )
    ]
    assert models == [
        "mijia.vacuum.b108za",
        "mijia.vacuum.b108zb",
        "mijia.vacuum.b108zh",
        "xiaomi.vacuum.b108gl",
    ]
    for index, model in enumerate(models):
        profile = next(
            item
            for item in robot_profiles()
            if item.model == model and not item.submodel
        )
        family = resolve_family(model)
        assert family is not None
        mac = f"00:00:00:00:00:{index + 1:02x}"
        robot = SpecRobot(model, profile.document(), mac=mac)
        robot.apply_family(family)
        with MiioEndpoint(robot):
            device = DreameVacuumDevice(
                "Lab",
                "127.0.0.1",
                _TOKEN,
                mac,
                account_type="mi",
                family_resolver=resolve_family,
                configured_model=model,
            )
            device.connect_device()
            try:
                device._request_properties()
                current = device.get_map(0)
                assert current is not None
                assert 1 in current.segments and 2 in current.segments
                image = DreameVacuumMapRenderer().render_map(
                    device.get_map_for_render(current)
                )
                _assert_rooms_fill_the_frame(image)
            finally:
                release_device(device)


def _assert_rooms_fill_the_frame(image: bytes) -> None:
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

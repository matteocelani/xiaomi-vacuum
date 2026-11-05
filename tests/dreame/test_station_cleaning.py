"""Mijia base-station cleaning stays available with the mop pads removed."""

from __future__ import annotations

from types import SimpleNamespace

from custom_components.dreame_vacuum.dreame.types import ACTION_AVAILABILITY


def _device(
    *, mijia: bool, mop_installed: bool, docked: bool = True, started: bool = False
) -> SimpleNamespace:
    return SimpleNamespace(
        status=SimpleNamespace(
            docked=docked,
            station_cleaning=False,
            water_tank_or_mop_installed=mop_installed,
            draining=False,
            self_repairing=False,
            started=started,
            paused=False,
            washing=False,
            washing_paused=False,
            drying=False,
            auto_emptying=False,
        ),
        capability=SimpleNamespace(washboard_cleaning_status=False, mijia=mijia),
    )


def test_mijia_station_cleaning_does_not_require_mop_pads() -> None:
    available = ACTION_AVAILABILITY["base_station_cleaning"]
    assert available(_device(mijia=True, mop_installed=False))
    assert not available(_device(mijia=False, mop_installed=False))
    assert available(_device(mijia=False, mop_installed=True))
    assert not available(_device(mijia=True, mop_installed=False, docked=False))
    assert not available(_device(mijia=True, mop_installed=False, started=True))

"""Vacuum-only stays available when a published spec includes Sweep."""

from __future__ import annotations

from types import SimpleNamespace

from custom_components.dreame_vacuum.dreame.const import (
    CLEANING_MODE_MOPPING,
    CLEANING_MODE_SWEEPING,
    CLEANING_MODE_SWEEPING_AND_MOPPING,
    SUCTION_LEVEL_CODE_TO_NAME,
)
from custom_components.dreame_vacuum.dreame.device import (
    DreameVacuumDevice,
    DreameVacuumDeviceStatus,
)
from custom_components.dreame_vacuum.dreame.exceptions import UnavailableException
from custom_components.dreame_vacuum.dreame.types import (
    PROPERTY_AVAILABILITY,
    DreameVacuumCleaningMode,
    DreameVacuumDeviceCapability,
    DreameVacuumProperty,
    DreameVacuumSuctionLevel,
    DreameVacuumTaskStatus,
)
from custom_components.dreame_vacuum.xiaomi.mapping import resolve_family
from custom_components.dreame_vacuum.xiaomi.model import StoredState
import pytest

_MOP_INSTALLED_MODES = [
    CLEANING_MODE_SWEEPING,
    CLEANING_MODE_MOPPING,
    CLEANING_MODE_SWEEPING_AND_MOPPING,
]
# Station models plus S20+. Each spec publishes Sweep as its own cleaning mode.
_PUBLISHED_SWEEP_MODELS = (
    "xiaomi.vacuum.d109gl",
    "xiaomi.vacuum.d102gl",
    "xiaomi.vacuum.ov31gl",
    "xiaomi.vacuum.b108gl",
)


def _device(model: str | None) -> DreameVacuumDevice:
    device = object.__new__(DreameVacuumDevice)
    family = None if model is None else resolve_family(model)
    shell = SimpleNamespace(
        info=SimpleNamespace(model=model or "dreame.vacuum.p2008", version=1),
        get_property=lambda _prop: None,
        _property_codec=family,
        _map_manager=None,
        status=SimpleNamespace(
            current_segments=None,
            current_map=None,
            selected_map=None,
            fill_light=None,
        ),
    )
    capability = DreameVacuumDeviceCapability(shell)
    if family is not None:
        family.apply_capabilities(capability)
    device.capability = capability
    device._property_codec = family
    device._map_manager = None
    device._update_callback = None
    device._property_update_callback = {}
    device._dirty_data = {}
    device._last_change = 0
    device._last_settings_request = 0
    device._ready = True
    device._previous_cleaning_mode = None
    device.schedule_update = lambda *_args, **_kwargs: None
    device.data = {}
    sent: list[tuple[int, int, object]] = []

    def record(siid: int, piid: int, value: object) -> list[dict[str, int]]:
        sent.append((siid, piid, value))
        return [{"code": 0}]

    device._protocol = SimpleNamespace(set_property=record)
    device.sent = sent
    if family is None:
        device.property_mapping = {
            DreameVacuumProperty.CLEANING_MODE: {"siid": 4, "piid": 23},
            DreameVacuumProperty.SUCTION_LEVEL: {"siid": 4, "piid": 4},
            DreameVacuumProperty.WATER_TANK: {"siid": 4, "piid": 6},
        }
    else:
        device.property_mapping = {
            DreameVacuumProperty[name]: dict(address)
            for name, address in family.property_overrides.items()
            if name in DreameVacuumProperty.__members__
        }
    device.status = DreameVacuumDeviceStatus(device)
    return device


def _park_with_mop(device: DreameVacuumDevice, cleaning_mode: int) -> None:
    device.data[DreameVacuumProperty.WATER_TANK.value] = True
    device.data[DreameVacuumProperty.CLEANING_MODE.value] = cleaning_mode
    device.data[DreameVacuumProperty.STATE.value] = int(StoredState.CHARGING)
    device.data[DreameVacuumProperty.CHARGING_STATUS.value] = 1
    device.data[DreameVacuumProperty.TASK_STATUS.value] = int(
        DreameVacuumTaskStatus.COMPLETED
    )
    device.status.cleaning_mode = DreameVacuumCleaningMode(cleaning_mode)


@pytest.mark.parametrize("model", _PUBLISHED_SWEEP_MODELS)
def test_published_sweep_stays_available_with_the_mop_installed(model: str) -> None:
    family = resolve_family(model)
    assert family is not None
    assert family.has_published_cleaning_mode(DreameVacuumCleaningMode.SWEEPING.value)
    device = _device(model)
    assert device.capability.mop_pad_lifting is False
    assert device.capability.sweep_with_mop is False
    _park_with_mop(device, DreameVacuumCleaningMode.SWEEPING_AND_MOPPING.value)
    device._water_tank_changed()
    assert list(device.status.cleaning_mode_list) == _MOP_INSTALLED_MODES


def test_x20_max_sweeping_writes_the_spec_sweep_value() -> None:
    device = _device("xiaomi.vacuum.d109gl")
    _park_with_mop(device, DreameVacuumCleaningMode.SWEEPING_AND_MOPPING.value)
    assert device.set_cleaning_mode(DreameVacuumCleaningMode.SWEEPING.value) is True
    assert device.get_property(DreameVacuumProperty.CLEANING_MODE) == 0
    mapping = device.property_mapping[DreameVacuumProperty.CLEANING_MODE]
    assert device.sent == [(mapping["siid"], mapping["piid"], 1)]
    device._cleaning_mode_changed()
    assert device.status.cleaning_mode is DreameVacuumCleaningMode.SWEEPING
    assert device.status.sweeping is True
    assert device.status.mopping is False
    assert PROPERTY_AVAILABILITY[DreameVacuumProperty.SUCTION_LEVEL.name](device)
    assert set(device.status.suction_level_list) == set(
        SUCTION_LEVEL_CODE_TO_NAME.values()
    )
    assert device.set_suction_level(DreameVacuumSuctionLevel.STANDARD.value) is True
    suction = device.property_mapping[DreameVacuumProperty.SUCTION_LEVEL]
    assert device.sent[-1] == (suction["siid"], suction["piid"], 2)


def test_mop_modes_still_write_when_the_mop_is_installed() -> None:
    device = _device("xiaomi.vacuum.d109gl")
    _park_with_mop(device, DreameVacuumCleaningMode.SWEEPING.value)
    mapping = device.property_mapping[DreameVacuumProperty.CLEANING_MODE]
    assert device.set_cleaning_mode(DreameVacuumCleaningMode.MOPPING.value) is True
    assert device.get_property(DreameVacuumProperty.CLEANING_MODE) == 1
    assert device.sent[-1] == (mapping["siid"], mapping["piid"], 2)
    device._cleaning_mode_changed()
    assert device.status.mopping is True
    assert (
        PROPERTY_AVAILABILITY[DreameVacuumProperty.SUCTION_LEVEL.name](device) is False
    )
    assert (
        device.set_cleaning_mode(DreameVacuumCleaningMode.SWEEPING_AND_MOPPING.value)
        is True
    )
    assert device.get_property(DreameVacuumProperty.CLEANING_MODE) == 2
    assert device.sent[-1] == (mapping["siid"], mapping["piid"], 3)
    device._cleaning_mode_changed()
    assert device.status.sweeping_and_mopping is True
    assert PROPERTY_AVAILABILITY[DreameVacuumProperty.SUCTION_LEVEL.name](device)


def test_removing_the_mop_leaves_vacuum_only() -> None:
    device = _device("xiaomi.vacuum.d109gl")
    _park_with_mop(device, DreameVacuumCleaningMode.SWEEPING.value)
    device.data[DreameVacuumProperty.WATER_TANK.value] = False
    device._water_tank_changed()
    assert list(device.status.cleaning_mode_list) == [CLEANING_MODE_SWEEPING]


@pytest.mark.parametrize("model", (None, "xiaomi.vacuum.b112"))
def test_sweeping_stays_hidden_when_the_spec_does_not_publish_it(
    model: str | None,
) -> None:
    device = _device(model)
    if model is not None:
        family = resolve_family(model)
        assert family is not None
        assert (
            family.has_published_cleaning_mode(DreameVacuumCleaningMode.SWEEPING.value)
            is False
        )
    _park_with_mop(device, DreameVacuumCleaningMode.SWEEPING_AND_MOPPING.value)
    device._water_tank_changed()
    assert CLEANING_MODE_SWEEPING not in device.status.cleaning_mode_list
    with pytest.raises(UnavailableException):
        device.set_cleaning_mode(DreameVacuumCleaningMode.SWEEPING.value)
    assert device.sent == []


def test_unpublished_stored_modes_stay_rejected() -> None:
    family = resolve_family("xiaomi.vacuum.d109gl")
    assert family is not None
    for stored in (0, 1, 2, 3):
        assert family.has_published_cleaning_mode(stored) is True
    assert family.has_published_cleaning_mode(4) is False
    roller = resolve_family("xiaomi.vacuum.pv11gl")
    assert roller is not None
    assert roller.has_published_cleaning_mode(0) is False

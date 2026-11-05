"""Reported model persistence stays inside Xiaomi families."""

from __future__ import annotations

from types import SimpleNamespace


def test_reported_model_is_stored_only_for_a_xiaomi_family(
    integration_package: object,
) -> None:
    del integration_package
    from custom_components.dreame_vacuum.coordinator import (
        DreameVacuumDataUpdateCoordinator,
    )

    coordinator = object.__new__(DreameVacuumDataUpdateCoordinator)
    updates: list[dict[str, str]] = []

    def update_entry(_entry: object, *, data: dict[str, str]) -> None:
        updates.append(data)

    coordinator.hass = SimpleNamespace(
        config_entries=SimpleNamespace(async_update_entry=update_entry)
    )

    def remember(model: str, data: dict[str, str]) -> None:
        updates.clear()
        coordinator._device = SimpleNamespace(info=SimpleNamespace(model=model))
        coordinator._entry = SimpleNamespace(data=data)
        coordinator._remember_reported_model()

    remember("dreame.vacuum.r2228", {})
    assert updates == []
    remember("xiaomi.vacuum.c102gl", {})
    assert updates == []
    remember("xiaomi.vacuum.b108gl", {})
    assert updates == [{"model": "xiaomi.vacuum.b108gl"}]
    remember("xiaomi.vacuum.b108gl", {"model": "xiaomi.vacuum.b108gl"})
    assert updates == []

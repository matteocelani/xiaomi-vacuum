"""Home Assistant entities for declarative Xiaomi controls."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.button import ButtonEntity
from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.components.switch import SwitchEntity
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import DreameVacuumDataUpdateCoordinator
from .dreame import (
    DeviceException,
    DeviceUnavailableException,
    DreameVacuumProperty,
)
from .entity import DreameVacuumEntity, DreameVacuumEntityDescription
from .xiaomi import (
    XiaomiControl,
    XiaomiControlException,
    controls_of,
    invoke_control,
    read_control,
    write_control,
)


def add_xiaomi_controls(
    coordinator: DreameVacuumDataUpdateCoordinator,
    async_add_entities: AddEntitiesCallback,
    domain: str,
) -> None:
    """Add the Xiaomi controls that belong to one platform."""
    matched = [
        control
        for control in controls_of(coordinator.device)
        if control.domain == domain
    ]
    if not matched:
        return
    kind = _ENTITY_TYPES.get(domain)
    if kind is None:
        return
    async_add_entities(kind(coordinator, control) for control in matched)


class _XiaomiEntity(DreameVacuumEntity):
    """Base for one declarative Xiaomi control."""

    # Home Assistant reads these attributes before the Dreame description, which
    # does not declare them. None means the control has no device class.
    _attr_device_class = None
    _attr_entity_registry_enabled_default = True
    _attr_entity_registry_visible_default = True
    _attr_force_update = False
    _attr_icon = None
    _attr_unit_of_measurement = None

    def __init__(
        self,
        coordinator: DreameVacuumDataUpdateCoordinator,
        control: XiaomiControl,
    ) -> None:
        self._control = control
        self._attr_entity_registry_enabled_default = control.enabled_by_default
        super().__init__(coordinator, DreameVacuumEntityDescription(key=control.key))
        self._attr_entity_category = (
            EntityCategory.DIAGNOSTIC if control.diagnostic else EntityCategory.CONFIG
        )
        self._attr_translation_placeholders = {}

    @property
    def available(self) -> bool:
        """Return whether the control has a value the spec allows."""
        if not self.device.device_connected:
            return False
        if self._control.domain == "button":
            return True
        if self._control.writable and not self._control.readable:
            return True
        return _known(self._control, self._raw())

    async def _commit(self, value: object) -> None:
        if not self.device.device_connected:
            self._raise_error(DeviceUnavailableException())
        try:
            await self.hass.async_add_executor_job(self._commit_blocking, value)
        except XiaomiControlException as exc:
            raise HomeAssistantError(
                translation_key="xiaomi_control_failed",
                translation_placeholders={"control": exc.key},
            ) from exc
        except DeviceException as exc:
            self._raise_error(exc)
        self.coordinator.async_set_updated_data()

    def _commit_blocking(self, value: object) -> None:
        control = self._control
        if control.property_name:
            self.device.set_property(DreameVacuumProperty[control.property_name], value)
            return
        write_control(self.device, control, value)

    def _raw(self) -> object:
        control = self._control
        if control.property_name:
            return self.device.get_property(DreameVacuumProperty[control.property_name])
        return read_control(self.device, control)


class XiaomiSwitch(_XiaomiEntity, SwitchEntity):
    """Boolean Xiaomi setting."""

    @property
    def is_on(self) -> bool:
        """Return whether the setting is enabled."""
        return self._raw() in (True, 1)

    async def async_turn_on(self, **_kwargs: object) -> None:
        """Enable the setting."""
        await self._commit(True)

    async def async_turn_off(self, **_kwargs: object) -> None:
        """Disable the setting."""
        await self._commit(False)


class XiaomiBinarySensor(_XiaomiEntity, BinarySensorEntity):
    """Read-only Xiaomi boolean."""

    @property
    def is_on(self) -> bool:
        """Return whether the reading is true."""
        return self._raw() in (True, 1)


class XiaomiNumber(_XiaomiEntity, NumberEntity):
    """Writable Xiaomi integer."""

    _attr_native_unit_of_measurement = None

    def __init__(
        self,
        coordinator: DreameVacuumDataUpdateCoordinator,
        control: XiaomiControl,
    ) -> None:
        super().__init__(coordinator, control)
        self._attr_mode = NumberMode.BOX
        if control.minimum is None or control.maximum is None:
            raise XiaomiControlException(control.key)
        self._attr_native_min_value = float(control.minimum)
        self._attr_native_max_value = float(control.maximum)
        self._attr_native_step = float(control.step)
        if control.unit:
            self._attr_native_unit_of_measurement = control.unit

    @property
    def native_value(self) -> int | None:
        """Return the integer currently stored for the control."""
        raw = self._raw()
        if isinstance(raw, bool) or not isinstance(raw, int):
            return None
        return raw

    async def async_set_native_value(self, value: float) -> None:
        """Write a new integer."""
        await self._commit(int(value))


class XiaomiSelect(_XiaomiEntity, SelectEntity):
    """Value-list Xiaomi setting."""

    def __init__(
        self,
        coordinator: DreameVacuumDataUpdateCoordinator,
        control: XiaomiControl,
    ) -> None:
        super().__init__(coordinator, control)
        self._attr_options = [slug for _value, slug in control.options]

    @property
    def current_option(self) -> str | None:
        """Return the slug for the current wire value."""
        raw = self._raw()
        if isinstance(raw, bool) or not isinstance(raw, int):
            return None
        return _slug(self._control, raw)

    async def async_select_option(self, option: str) -> None:
        """Write the wire value for one option."""
        for value, slug in self._control.options:
            if slug == option:
                await self._commit(value)
                return
        raise HomeAssistantError(
            translation_key="xiaomi_control_failed",
            translation_placeholders={"control": self._control.key},
        )


class XiaomiSensor(_XiaomiEntity, SensorEntity):
    """Read-only Xiaomi measurement or status."""

    _attr_state_class = None
    _attr_last_reset = None
    _attr_options = None
    _attr_suggested_display_precision = None
    _attr_native_unit_of_measurement = None
    _attr_suggested_unit_of_measurement = None

    def __init__(
        self,
        coordinator: DreameVacuumDataUpdateCoordinator,
        control: XiaomiControl,
    ) -> None:
        super().__init__(coordinator, control)
        if control.unit:
            self._attr_native_unit_of_measurement = control.unit
        if control.value_kind == "enum":
            self._attr_device_class = SensorDeviceClass.ENUM
            self._attr_options = [slug for _value, slug in control.options]

    @property
    def native_value(self) -> int | str | None:
        """Return the measurement or the status slug."""
        raw = self._raw()
        if self._control.value_kind == "enum":
            if isinstance(raw, bool) or not isinstance(raw, int):
                return None
            return _slug(self._control, raw)
        if self._control.value_kind == "string":
            return raw if isinstance(raw, str) else None
        if isinstance(raw, bool) or not isinstance(raw, int):
            return None
        return raw


class XiaomiButton(_XiaomiEntity, ButtonEntity):
    """Parameter-free Xiaomi action."""

    async def async_press(self) -> None:
        """Invoke the action with an empty parameter list."""
        if not self.device.device_connected:
            self._raise_error(DeviceUnavailableException())
        try:
            await self.hass.async_add_executor_job(
                invoke_control, self.device, self._control
            )
        except XiaomiControlException as exc:
            raise HomeAssistantError(
                translation_key="xiaomi_control_failed",
                translation_placeholders={"control": exc.key},
            ) from exc
        except DeviceException as exc:
            self._raise_error(exc)
        self.coordinator.async_set_updated_data()


_ENTITY_TYPES = {
    "switch": XiaomiSwitch,
    "binary_sensor": XiaomiBinarySensor,
    "number": XiaomiNumber,
    "select": XiaomiSelect,
    "sensor": XiaomiSensor,
    "button": XiaomiButton,
}


def _slug(control: XiaomiControl, wire: int) -> str | None:
    for value, slug in control.options:
        if value == wire:
            return slug
    return None


def _known(control: XiaomiControl, raw: object) -> bool:
    if control.value_kind == "bool":
        return raw in (True, False, 0, 1)
    if control.value_kind == "enum":
        return (
            isinstance(raw, int)
            and not isinstance(raw, bool)
            and _slug(control, raw) is not None
        )
    if control.value_kind == "int":
        return isinstance(raw, int) and not isinstance(raw, bool)
    if control.value_kind == "string":
        return isinstance(raw, str)
    return False

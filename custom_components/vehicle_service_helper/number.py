from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_DISTANCE_UNIT, DOMAIN
from .coordinator import (
    VehicleServiceCoordinator,
    get_current_odometer,
    get_technical_inspection_interval_days,
)
from .entity import VehicleServiceCoordinatorEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: VehicleServiceCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            VehicleOdometerNumber(coordinator),
            VehicleTechnicalInspectionIntervalDaysNumber(coordinator),
        ],
        True,
    )


class VehicleOdometerNumber(VehicleServiceCoordinatorEntity, NumberEntity):
    _attr_name = "Odometer"
    _attr_has_entity_name = True
    _attr_native_min_value = 0
    _attr_native_step = 1
    _attr_mode = NumberMode.BOX

    def __init__(self, coordinator: VehicleServiceCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_odometer"
        unit = coordinator.entry.data.get(CONF_DISTANCE_UNIT, "km")
        self._attr_native_unit_of_measurement = unit

    @property
    def native_value(self) -> float:
        return get_current_odometer(self.coordinator.entry)

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.async_set_odometer(float(value))


class VehicleTechnicalInspectionIntervalDaysNumber(
    VehicleServiceCoordinatorEntity, NumberEntity
):
    _attr_name = "Technical Inspection Interval"
    _attr_has_entity_name = True
    _attr_native_min_value = 1
    _attr_native_step = 1
    _attr_native_unit_of_measurement = "d"
    _attr_mode = NumberMode.BOX

    def __init__(self, coordinator: VehicleServiceCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = (
            f"{coordinator.entry.entry_id}_technical_inspection_interval_days"
        )

    @property
    def native_value(self) -> float | None:
        interval_days = get_technical_inspection_interval_days(self.coordinator.entry)
        return float(interval_days) if interval_days is not None else None

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.async_set_technical_inspection(interval_days=int(value))

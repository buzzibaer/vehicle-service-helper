from __future__ import annotations

from datetime import date

from homeassistant.components.date import DateEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import (
    VehicleServiceCoordinator,
    get_technical_inspection_last_date,
)
from .entity import VehicleServiceCoordinatorEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: VehicleServiceCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([VehicleTechnicalInspectionLastDate(coordinator)], True)


class VehicleTechnicalInspectionLastDate(VehicleServiceCoordinatorEntity, DateEntity):
    _attr_name = "Technical Inspection Last Date"
    _attr_has_entity_name = True

    def __init__(self, coordinator: VehicleServiceCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_technical_inspection_last_date"

    @property
    def native_value(self) -> date | None:
        return get_technical_inspection_last_date(self.coordinator.entry)

    async def async_set_value(self, value: date) -> None:
        await self.coordinator.async_set_technical_inspection(last_inspection_date=value)

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_DISTANCE_UNIT, DOMAIN
from .coordinator import VehicleServiceCoordinator
from .entity import VehicleServiceCoordinatorEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: VehicleServiceCoordinator = hass.data[DOMAIN][entry.entry_id]
    unit = entry.data.get(CONF_DISTANCE_UNIT, "km")
    async_add_entities(
        [
            OdometerAdjustButton(coordinator, 100, unit),
            OdometerAdjustButton(coordinator, 500, unit),
        ]
    )


class OdometerAdjustButton(VehicleServiceCoordinatorEntity, ButtonEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator: VehicleServiceCoordinator, delta: int, unit: str) -> None:
        super().__init__(coordinator)
        self._delta = delta
        self._attr_name = f"Increase Odometer +{delta} {unit}"
        self._attr_unique_id = f"{coordinator.entry.entry_id}_odometer_plus_{delta}"

    async def async_press(self) -> None:
        await self.coordinator.async_adjust_odometer(self._delta)

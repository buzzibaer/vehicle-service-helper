from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, OPTION_TEMPLATES, TEMPLATE_ID, TEMPLATE_NAME
from .coordinator import VehicleServiceCoordinator
from .entity import VehicleServiceCoordinatorEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: VehicleServiceCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[BinarySensorEntity] = []

    for template in entry.options.get(OPTION_TEMPLATES, []):
        entities.append(TemplateServiceDueBinarySensor(coordinator, template))

    async_add_entities(entities)


class TemplateServiceDueBinarySensor(VehicleServiceCoordinatorEntity, BinarySensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator: VehicleServiceCoordinator, template: dict[str, Any]) -> None:
        super().__init__(coordinator)
        self._template_id = template[TEMPLATE_ID]
        self._attr_name = f"{template[TEMPLATE_NAME]} Service Due"
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{self._template_id}_service_due"

    @property
    def is_on(self) -> bool:
        if not self.coordinator.data:
            return False
        return bool(self.coordinator.data.get(self._template_id, {}).get("is_due", False))

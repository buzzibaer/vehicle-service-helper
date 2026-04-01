from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    COORDINATOR_VEHICLE_KEY,
    CONF_DISTANCE_UNIT,
    DOMAIN,
    OPTION_TEMPLATES,
    STATUS_DUE_SOON,
    STATUS_OK,
    STATUS_OVERDUE,
    TEMPLATE_ID,
    TEMPLATE_MILEAGE_INTERVAL,
    TEMPLATE_NAME,
    TEMPLATE_TIME_INTERVAL_MONTHS,
)
from .coordinator import VehicleServiceCoordinator
from .entity import VehicleServiceCoordinatorEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: VehicleServiceCoordinator = hass.data[DOMAIN][entry.entry_id]
    templates = entry.options.get(OPTION_TEMPLATES, [])
    entities: list[SensorEntity] = []

    entities.append(VehicleTechnicalInspectionDateSensor(coordinator))
    entities.append(VehicleTechnicalInspectionRemainingDaysSensor(coordinator))

    for template in templates:
        template_id = template[TEMPLATE_ID]
        entities.append(TemplateStatusSensor(coordinator, template))

        if template.get(TEMPLATE_MILEAGE_INTERVAL):
            entities.append(TemplateRemainingDistanceSensor(coordinator, template_id, template))
        if template.get(TEMPLATE_TIME_INTERVAL_MONTHS):
            entities.append(TemplateRemainingDaysSensor(coordinator, template_id, template))

    async_add_entities(entities)


class VehicleTechnicalInspectionDateSensor(VehicleServiceCoordinatorEntity, SensorEntity):
    _attr_name = "Technical Inspection Next Date"
    _attr_has_entity_name = True

    def __init__(self, coordinator: VehicleServiceCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_technical_inspection_next_date"

    @property
    def native_value(self) -> str | None:
        vehicle_data = self.coordinator.data.get(COORDINATOR_VEHICLE_KEY, {})
        return vehicle_data.get("next_inspection_date")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        vehicle_data = self.coordinator.data.get(COORDINATOR_VEHICLE_KEY, {})
        return {
            "last_inspection_date": vehicle_data.get("last_inspection_date"),
            "inspection_interval_days": vehicle_data.get("interval_days"),
            "remaining_days": vehicle_data.get("remaining_days"),
            "is_overdue": vehicle_data.get("is_overdue", False),
        }


class VehicleTechnicalInspectionRemainingDaysSensor(
    VehicleServiceCoordinatorEntity, SensorEntity
):
    _attr_name = "Technical Inspection Remaining Days"
    _attr_native_unit_of_measurement = "d"
    _attr_has_entity_name = True

    def __init__(self, coordinator: VehicleServiceCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = (
            f"{coordinator.entry.entry_id}_technical_inspection_remaining_days"
        )

    @property
    def native_value(self) -> int | None:
        vehicle_data = self.coordinator.data.get(COORDINATOR_VEHICLE_KEY, {})
        return vehicle_data.get("remaining_days")


class TemplateBaseSensor(VehicleServiceCoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: VehicleServiceCoordinator,
        template_id: str,
        kind: str,
    ) -> None:
        super().__init__(coordinator)
        self._template_id = template_id
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{template_id}_{kind}"

    @property
    def _template_data(self) -> dict[str, Any]:
        return self.coordinator.data.get(self._template_id, {}) if self.coordinator.data else {}


class TemplateStatusSensor(TemplateBaseSensor):
    _attr_options = [STATUS_OK, STATUS_DUE_SOON, STATUS_OVERDUE]

    def __init__(self, coordinator: VehicleServiceCoordinator, template: dict[str, Any]) -> None:
        self._attr_name = f"{template[TEMPLATE_NAME]} Status"
        super().__init__(
            coordinator,
            template[TEMPLATE_ID],
            "status",
        )

    @property
    def native_value(self) -> str:
        return self._template_data.get("status", STATUS_OK)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "next_due_odometer": self._template_data.get("next_due_odometer"),
            "next_due_date": self._template_data.get("next_due_date"),
            "remaining_distance": self._template_data.get("remaining_distance"),
            "remaining_days": self._template_data.get("remaining_days"),
            "last_service_date": self._template_data.get("last_service_date"),
            "last_service_odometer": self._template_data.get("last_service_odometer"),
        }


class TemplateRemainingDistanceSensor(TemplateBaseSensor):
    def __init__(
        self,
        coordinator: VehicleServiceCoordinator,
        template_id: str,
        template: dict[str, Any],
    ) -> None:
        self._attr_name = f"{template[TEMPLATE_NAME]} Remaining Distance"
        self._attr_native_unit_of_measurement = coordinator.entry.data.get(
            CONF_DISTANCE_UNIT, "km"
        )
        super().__init__(
            coordinator,
            template_id,
            "remaining_distance",
        )

    @property
    def native_value(self) -> int | None:
        return self._template_data.get("remaining_distance")


class TemplateRemainingDaysSensor(TemplateBaseSensor):
    _attr_native_unit_of_measurement = "d"

    def __init__(
        self,
        coordinator: VehicleServiceCoordinator,
        template_id: str,
        template: dict[str, Any],
    ) -> None:
        self._attr_name = f"{template[TEMPLATE_NAME]} Remaining Days"
        super().__init__(coordinator, template_id, "remaining_days")

    @property
    def native_value(self) -> int | None:
        return self._template_data.get("remaining_days")

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_LICENSE_PLATE, CONF_VEHICLE_NAME, DOMAIN
from .coordinator import VehicleServiceCoordinator


class VehicleServiceCoordinatorEntity(CoordinatorEntity[VehicleServiceCoordinator]):
    def __init__(self, coordinator: VehicleServiceCoordinator) -> None:
        super().__init__(coordinator)
        self._entry = coordinator.entry

    @property
    def device_info(self) -> DeviceInfo:
        vehicle_name = self._entry.data.get(CONF_VEHICLE_NAME, "Vehicle")
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=vehicle_name,
            model="Vehicle",
            manufacturer="Vehicle Service Helper",
            serial_number=self._entry.data.get(CONF_LICENSE_PLATE, None),
        )

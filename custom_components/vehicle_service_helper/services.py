from __future__ import annotations

from datetime import date

import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .const import (
    ATTR_ENTRY_ID,
    ATTR_ODOMETER,
    ATTR_OVERRIDE,
    ATTR_SERVICE_DATE,
    ATTR_TEMPLATE_ID,
    DOMAIN,
    SERVICE_MARK_SERVICE_DONE,
    SERVICE_SET_ODOMETER,
)
from .coordinator import VehicleServiceCoordinator


def _get_entry_and_coordinator(
    hass: HomeAssistant, entry_id: str
) -> VehicleServiceCoordinator:
    entry = hass.config_entries.async_get_entry(entry_id)
    if entry is None:
        raise ValueError("unknown_entry")

    domain_data = hass.data.get(DOMAIN, {})
    coordinator = domain_data.get(entry_id)
    if coordinator is None:
        raise ValueError("entry_not_loaded")
    return coordinator


async def async_register_services(hass: HomeAssistant) -> None:
    if hass.services.has_service(DOMAIN, SERVICE_SET_ODOMETER):
        return

    async def handle_set_odometer(call: ServiceCall) -> None:
        coordinator = _get_entry_and_coordinator(hass, call.data[ATTR_ENTRY_ID])
        await coordinator.async_set_odometer(
            float(call.data[ATTR_ODOMETER]),
            override=bool(call.data.get(ATTR_OVERRIDE, False)),
        )

    async def handle_mark_service_done(call: ServiceCall) -> None:
        coordinator = _get_entry_and_coordinator(hass, call.data[ATTR_ENTRY_ID])
        service_date: date | None = None
        if ATTR_SERVICE_DATE in call.data and call.data[ATTR_SERVICE_DATE]:
            service_date = date.fromisoformat(call.data[ATTR_SERVICE_DATE])
        odometer = call.data.get(ATTR_ODOMETER)

        await coordinator.async_mark_service_done(
            call.data[ATTR_TEMPLATE_ID],
            service_date=service_date,
            odometer=float(odometer) if odometer is not None else None,
        )

    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_ODOMETER,
        handle_set_odometer,
        schema=vol.Schema(
            {
                vol.Required(ATTR_ENTRY_ID): cv.string,
                vol.Required(ATTR_ODOMETER): vol.Coerce(float),
                vol.Optional(ATTR_OVERRIDE, default=False): bool,
            }
        ),
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_MARK_SERVICE_DONE,
        handle_mark_service_done,
        schema=vol.Schema(
            {
                vol.Required(ATTR_ENTRY_ID): cv.string,
                vol.Required(ATTR_TEMPLATE_ID): cv.string,
                vol.Optional(ATTR_SERVICE_DATE): cv.string,
                vol.Optional(ATTR_ODOMETER): vol.Coerce(float),
            }
        ),
    )


async def async_unregister_services(hass: HomeAssistant) -> None:
    if hass.services.has_service(DOMAIN, SERVICE_SET_ODOMETER):
        hass.services.async_remove(DOMAIN, SERVICE_SET_ODOMETER)
    if hass.services.has_service(DOMAIN, SERVICE_MARK_SERVICE_DONE):
        hass.services.async_remove(DOMAIN, SERVICE_MARK_SERVICE_DONE)

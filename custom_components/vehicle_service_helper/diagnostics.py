from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from .const import CONF_LICENSE_PLATE, DOMAIN

TO_REDACT = {CONF_LICENSE_PLATE}


def _build_diagnostics_payload(
    *,
    entry_data: dict[str, Any],
    option_data: dict[str, Any],
    coordinator_data: dict[str, Any],
    devices: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "entry": entry_data,
        "options": option_data,
        "coordinator_data": coordinator_data,
        "devices": devices,
    }


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
) -> dict[str, Any]:
    domain_data = hass.data.get(DOMAIN, {})
    coordinator = domain_data.get(config_entry.entry_id)

    devices = []
    device_registry = dr.async_get(hass)
    for device_entry in dr.async_entries_for_config_entry(device_registry, config_entry.entry_id):
        devices.append(
            {
                "id": device_entry.id,
                "name": device_entry.name,
                "model": device_entry.model,
                "manufacturer": device_entry.manufacturer,
            }
        )

    payload = _build_diagnostics_payload(
        entry_data=dict(config_entry.data),
        option_data=dict(config_entry.options),
        coordinator_data=coordinator.data if coordinator else {},
        devices=devices,
    )
    return async_redact_data(payload, TO_REDACT)

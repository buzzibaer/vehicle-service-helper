from __future__ import annotations

from datetime import date, timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from .const import (
    COORDINATOR_VEHICLE_KEY,
    DEFAULT_ODOMETER,
    OPTION_CURRENT_ODOMETER,
    OPTION_TECHNICAL_INSPECTION_INTERVAL_DAYS,
    OPTION_TECHNICAL_INSPECTION_LAST_DATE,
    OPTION_TEMPLATES,
    TEMPLATE_ID,
    TEMPLATE_LAST_SERVICE_DATE,
    TEMPLATE_LAST_SERVICE_ODOMETER,
)
from .reminder_engine import compute_template_status, compute_technical_inspection_status

_LOGGER = logging.getLogger(__name__)


def get_templates(entry: ConfigEntry) -> list[dict[str, Any]]:
    return list(entry.options.get(OPTION_TEMPLATES, []))


def get_current_odometer(entry: ConfigEntry) -> float:
    value = entry.options.get(OPTION_CURRENT_ODOMETER, DEFAULT_ODOMETER)
    try:
        return float(value)
    except (TypeError, ValueError):
        return DEFAULT_ODOMETER


def get_technical_inspection_last_date(entry: ConfigEntry) -> date | None:
    value = entry.options.get(OPTION_TECHNICAL_INSPECTION_LAST_DATE)
    if not isinstance(value, str):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def get_technical_inspection_interval_days(entry: ConfigEntry) -> int | None:
    value = entry.options.get(OPTION_TECHNICAL_INSPECTION_INTERVAL_DAYS)
    try:
        interval_days = int(value)
    except (TypeError, ValueError):
        return None
    return interval_days if interval_days > 0 else None


class VehicleServiceCoordinator(DataUpdateCoordinator[dict[str, dict[str, Any]]]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.entry = entry
        super().__init__(
            hass,
            _LOGGER,
            name=f"vehicle_service_helper_{entry.entry_id}",
            update_interval=timedelta(hours=12),
        )

    async def _async_update_data(self) -> dict[str, dict[str, Any]]:
        templates = get_templates(self.entry)
        current_odometer = get_current_odometer(self.entry)
        today = dt_util.now().date()

        computed: dict[str, dict[str, Any]] = {}
        computed[COORDINATOR_VEHICLE_KEY] = compute_technical_inspection_status(
            last_inspection_date_iso=self.entry.options.get(
                OPTION_TECHNICAL_INSPECTION_LAST_DATE
            ),
            interval_days=self.entry.options.get(OPTION_TECHNICAL_INSPECTION_INTERVAL_DAYS),
            today=today,
        )
        for template in templates:
            template_id = template[TEMPLATE_ID]
            computed[template_id] = compute_template_status(
                template=template,
                current_odometer=current_odometer,
                today=today,
            )
        return computed

    async def async_set_odometer(self, odometer: float, *, override: bool = False) -> None:
        current_odometer = get_current_odometer(self.entry)
        if not override and odometer < current_odometer:
            raise ValueError("odometer_rollback_not_allowed")

        options = dict(self.entry.options)
        options[OPTION_CURRENT_ODOMETER] = float(odometer)
        self.hass.config_entries.async_update_entry(self.entry, options=options)
        refreshed_entry = self.hass.config_entries.async_get_entry(self.entry.entry_id)
        if refreshed_entry is not None:
            self.entry = refreshed_entry
        await self.async_request_refresh()

    async def async_set_technical_inspection(
        self,
        *,
        last_inspection_date: date | None = None,
        interval_days: int | None = None,
    ) -> None:
        options = dict(self.entry.options)

        if last_inspection_date is not None:
            options[OPTION_TECHNICAL_INSPECTION_LAST_DATE] = last_inspection_date.isoformat()

        if interval_days is not None:
            if interval_days <= 0 or interval_days > 999:
                raise ValueError("inspection_interval_must_be_positive")
            options[OPTION_TECHNICAL_INSPECTION_INTERVAL_DAYS] = int(interval_days)

        self.hass.config_entries.async_update_entry(self.entry, options=options)
        refreshed_entry = self.hass.config_entries.async_get_entry(self.entry.entry_id)
        if refreshed_entry is not None:
            self.entry = refreshed_entry
        await self.async_request_refresh()

    async def async_adjust_odometer(self, delta: float) -> None:
        await self.async_set_odometer(get_current_odometer(self.entry) + delta, override=True)

    async def async_mark_service_done(
        self,
        template_id: str,
        *,
        service_date: date | None = None,
        odometer: float | None = None,
    ) -> None:
        templates = get_templates(self.entry)
        date_value = (service_date or dt_util.now().date()).isoformat()
        odometer_value = (
            float(odometer)
            if odometer is not None
            else float(get_current_odometer(self.entry))
        )

        updated_templates: list[dict[str, Any]] = []
        found = False
        for template in templates:
            if template[TEMPLATE_ID] != template_id:
                updated_templates.append(template)
                continue

            found = True
            updated = dict(template)
            updated[TEMPLATE_LAST_SERVICE_DATE] = date_value
            updated[TEMPLATE_LAST_SERVICE_ODOMETER] = odometer_value
            updated_templates.append(updated)

        if not found:
            raise ValueError("unknown_template")

        options = dict(self.entry.options)
        options[OPTION_TEMPLATES] = updated_templates
        if odometer is not None:
            current_odometer = get_current_odometer(self.entry)
            if odometer_value < current_odometer:
                raise ValueError("odometer_rollback_not_allowed")
            options[OPTION_CURRENT_ODOMETER] = odometer_value

        self.hass.config_entries.async_update_entry(self.entry, options=options)
        refreshed_entry = self.hass.config_entries.async_get_entry(self.entry.entry_id)
        if refreshed_entry is not None:
            self.entry = refreshed_entry
        await self.async_request_refresh()

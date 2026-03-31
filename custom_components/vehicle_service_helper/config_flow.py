from __future__ import annotations

from datetime import date
from typing import Any
from uuid import uuid4

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers import config_validation as cv

from .const import (
    CONF_DISTANCE_UNIT,
    CONF_LICENSE_PLATE,
    CONF_VEHICLE_NAME,
    DEFAULT_DISTANCE_UNIT,
    DEFAULT_ODOMETER,
    DOMAIN,
    OPTION_CURRENT_ODOMETER,
    OPTION_TEMPLATES,
    TEMPLATE_DUE_SOON_DAYS,
    TEMPLATE_DUE_SOON_DISTANCE,
    TEMPLATE_ENABLED,
    TEMPLATE_ICON,
    TEMPLATE_ID,
    TEMPLATE_LAST_SERVICE_DATE,
    TEMPLATE_LAST_SERVICE_ODOMETER,
    TEMPLATE_MILEAGE_INTERVAL,
    TEMPLATE_NAME,
    TEMPLATE_TIME_INTERVAL_MONTHS,
)


def _normalize_positive_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    number = int(value)
    if number == 0:
        return None
    if number < 0:
        raise ValueError("value_must_be_positive")
    return number


def _template_schema(defaults: dict[str, Any] | None = None) -> vol.Schema:
    defaults = defaults or {}
    return vol.Schema(
        {
            vol.Required(TEMPLATE_NAME, default=defaults.get(TEMPLATE_NAME, "")): cv.string,
            vol.Optional(TEMPLATE_ICON, default=defaults.get(TEMPLATE_ICON, "mdi:wrench")): cv.string,
            vol.Optional(
                TEMPLATE_MILEAGE_INTERVAL,
                default=defaults.get(TEMPLATE_MILEAGE_INTERVAL) or 0,
            ): vol.Coerce(int),
            vol.Optional(
                TEMPLATE_TIME_INTERVAL_MONTHS,
                default=defaults.get(TEMPLATE_TIME_INTERVAL_MONTHS) or 0,
            ): vol.Coerce(int),
            vol.Optional(
                TEMPLATE_DUE_SOON_DISTANCE,
                default=defaults.get(TEMPLATE_DUE_SOON_DISTANCE, 500),
            ): vol.Coerce(int),
            vol.Optional(
                TEMPLATE_DUE_SOON_DAYS,
                default=defaults.get(TEMPLATE_DUE_SOON_DAYS, 14),
            ): vol.Coerce(int),
            vol.Optional(
                TEMPLATE_LAST_SERVICE_ODOMETER,
                default=defaults.get(TEMPLATE_LAST_SERVICE_ODOMETER, 0),
            ): vol.Coerce(float),
            vol.Optional(
                TEMPLATE_LAST_SERVICE_DATE,
                default=defaults.get(TEMPLATE_LAST_SERVICE_DATE, date.today().isoformat()),
            ): cv.string,
            vol.Optional(TEMPLATE_ENABLED, default=defaults.get(TEMPLATE_ENABLED, True)): bool,
        }
    )


class VehicleServiceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_VEHICLE_NAME].strip().lower())
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=user_input[CONF_VEHICLE_NAME],
                data={
                    CONF_VEHICLE_NAME: user_input[CONF_VEHICLE_NAME],
                    CONF_DISTANCE_UNIT: user_input[CONF_DISTANCE_UNIT],
                    CONF_LICENSE_PLATE: user_input.get(CONF_LICENSE_PLATE, ""),
                },
                options={
                    OPTION_CURRENT_ODOMETER: DEFAULT_ODOMETER,
                    OPTION_TEMPLATES: [],
                },
            )

        schema = vol.Schema(
            {
                vol.Required(CONF_VEHICLE_NAME): cv.string,
                vol.Required(CONF_DISTANCE_UNIT, default=DEFAULT_DISTANCE_UNIT): vol.In(
                    ["km", "mi"]
                ),
                vol.Optional(CONF_LICENSE_PLATE, default=""): cv.string,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema)

    @staticmethod
    def async_get_options_flow(config_entry):
        return VehicleServiceOptionsFlow(config_entry)


class VehicleServiceOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry) -> None:
        self._config_entry = config_entry
        self._selected_template_id: str | None = None

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        templates = self._get_templates()
        menu_options = ["add_template"]
        if templates:
            menu_options.extend(["edit_template_select", "remove_template"])
        return self.async_show_menu(step_id="init", menu_options=menu_options)

    async def async_step_add_template(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}
        if user_input is not None:
            normalized, errors = self._validate_template_input(user_input)
            if not errors:
                templates = self._get_templates()
                normalized[TEMPLATE_ID] = uuid4().hex[:8]
                templates.append(normalized)
                return self._create_options_entry(templates)

        return self.async_show_form(
            step_id="add_template",
            data_schema=_template_schema(),
            errors=errors,
        )

    async def async_step_edit_template_select(
        self, user_input: dict[str, Any] | None = None
    ):
        template_choices = {
            template[TEMPLATE_ID]: template[TEMPLATE_NAME] for template in self._get_templates()
        }
        if user_input is not None:
            self._selected_template_id = user_input[TEMPLATE_ID]
            return await self.async_step_edit_template()

        return self.async_show_form(
            step_id="edit_template_select",
            data_schema=vol.Schema(
                {vol.Required(TEMPLATE_ID): vol.In(template_choices)}
            ),
        )

    async def async_step_edit_template(self, user_input: dict[str, Any] | None = None):
        template = self._find_selected_template()
        if template is None:
            return await self.async_step_init()

        errors: dict[str, str] = {}
        if user_input is not None:
            normalized, errors = self._validate_template_input(user_input)
            if not errors:
                normalized[TEMPLATE_ID] = template[TEMPLATE_ID]
                templates = [
                    normalized if item[TEMPLATE_ID] == self._selected_template_id else item
                    for item in self._get_templates()
                ]
                return self._create_options_entry(templates)

        return self.async_show_form(
            step_id="edit_template",
            data_schema=_template_schema(template),
            errors=errors,
        )

    async def async_step_remove_template(self, user_input: dict[str, Any] | None = None):
        template_choices = {
            template[TEMPLATE_ID]: template[TEMPLATE_NAME] for template in self._get_templates()
        }
        if user_input is not None:
            template_id = user_input[TEMPLATE_ID]
            templates = [
                item for item in self._get_templates() if item[TEMPLATE_ID] != template_id
            ]
            return self._create_options_entry(templates)

        return self.async_show_form(
            step_id="remove_template",
            data_schema=vol.Schema(
                {vol.Required(TEMPLATE_ID): vol.In(template_choices)}
            ),
        )

    def _get_templates(self) -> list[dict[str, Any]]:
        return list(self._config_entry.options.get(OPTION_TEMPLATES, []))

    def _find_selected_template(self) -> dict[str, Any] | None:
        if self._selected_template_id is None:
            return None
        for template in self._get_templates():
            if template[TEMPLATE_ID] == self._selected_template_id:
                return template
        return None

    def _validate_template_input(
        self, user_input: dict[str, Any]
    ) -> tuple[dict[str, Any], dict[str, str]]:
        errors: dict[str, str] = {}
        normalized: dict[str, Any] = {
            TEMPLATE_NAME: user_input[TEMPLATE_NAME].strip(),
            TEMPLATE_ICON: user_input.get(TEMPLATE_ICON, "mdi:wrench"),
            TEMPLATE_ENABLED: bool(user_input.get(TEMPLATE_ENABLED, True)),
        }

        try:
            mileage_interval = _normalize_positive_int(
                user_input.get(TEMPLATE_MILEAGE_INTERVAL)
            )
            time_interval_months = _normalize_positive_int(
                user_input.get(TEMPLATE_TIME_INTERVAL_MONTHS)
            )
            due_soon_distance = max(0, int(user_input.get(TEMPLATE_DUE_SOON_DISTANCE, 0)))
            due_soon_days = max(0, int(user_input.get(TEMPLATE_DUE_SOON_DAYS, 0)))
            last_service_odometer = float(user_input.get(TEMPLATE_LAST_SERVICE_ODOMETER, 0))
            last_service_date = user_input.get(TEMPLATE_LAST_SERVICE_DATE)
            if normalized[TEMPLATE_NAME] == "":
                errors["base"] = "name_required"
            if mileage_interval is None and time_interval_months is None:
                errors["base"] = "interval_required"
            if last_service_date:
                date.fromisoformat(last_service_date)
        except ValueError:
            errors["base"] = "invalid_template"
            return normalized, errors

        normalized[TEMPLATE_MILEAGE_INTERVAL] = mileage_interval
        normalized[TEMPLATE_TIME_INTERVAL_MONTHS] = time_interval_months
        normalized[TEMPLATE_DUE_SOON_DISTANCE] = due_soon_distance
        normalized[TEMPLATE_DUE_SOON_DAYS] = due_soon_days
        normalized[TEMPLATE_LAST_SERVICE_ODOMETER] = last_service_odometer
        normalized[TEMPLATE_LAST_SERVICE_DATE] = last_service_date
        return normalized, errors

    def _create_options_entry(self, templates: list[dict[str, Any]]):
        options = dict(self._config_entry.options)
        options[OPTION_TEMPLATES] = templates
        options.setdefault(OPTION_CURRENT_ODOMETER, DEFAULT_ODOMETER)
        return self.async_create_entry(title="", data=options)

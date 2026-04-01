from custom_components.vehicle_service_helper.config_flow import (
    VehicleServiceOptionsFlow,
    _vehicle_inspection_schema,
    _normalize_positive_int,
)
from voluptuous import MultipleInvalid
from custom_components.vehicle_service_helper.const import (
    OPTION_TEMPLATES,
    TEMPLATE_DUE_SOON_DAYS,
    TEMPLATE_DUE_SOON_DISTANCE,
    TEMPLATE_ENABLED,
    TEMPLATE_ICON,
    TEMPLATE_LAST_SERVICE_DATE,
    TEMPLATE_LAST_SERVICE_ODOMETER,
    TEMPLATE_MILEAGE_INTERVAL,
    TEMPLATE_NAME,
    TEMPLATE_TIME_INTERVAL_MONTHS,
)


class _DummyEntry:
    def __init__(self) -> None:
        self.options = {OPTION_TEMPLATES: []}


def test_normalize_positive_int_allows_none_and_zero() -> None:
    assert _normalize_positive_int(None) is None
    assert _normalize_positive_int("") is None
    assert _normalize_positive_int(0) is None
    assert _normalize_positive_int("0") is None


def test_normalize_positive_int_rejects_negative() -> None:
    try:
        _normalize_positive_int(-1)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError for negative integer")


def test_validate_template_requires_name_and_interval() -> None:
    flow = VehicleServiceOptionsFlow(_DummyEntry())
    normalized, errors = flow._validate_template_input(
        {
            TEMPLATE_NAME: "",
            TEMPLATE_ICON: "mdi:wrench",
            TEMPLATE_MILEAGE_INTERVAL: 0,
            TEMPLATE_TIME_INTERVAL_MONTHS: 0,
            TEMPLATE_DUE_SOON_DISTANCE: 500,
            TEMPLATE_DUE_SOON_DAYS: 14,
            TEMPLATE_LAST_SERVICE_ODOMETER: 10000,
            TEMPLATE_LAST_SERVICE_DATE: "2026-03-31",
            TEMPLATE_ENABLED: True,
        }
    )

    assert TEMPLATE_NAME in normalized
    assert errors["base"] in {"name_required", "interval_required"}


def test_validate_template_accepts_mileage_only() -> None:
    flow = VehicleServiceOptionsFlow(_DummyEntry())
    normalized, errors = flow._validate_template_input(
        {
            TEMPLATE_NAME: "Oil Change",
            TEMPLATE_ICON: "mdi:oil",
            TEMPLATE_MILEAGE_INTERVAL: 10000,
            TEMPLATE_TIME_INTERVAL_MONTHS: 0,
            TEMPLATE_DUE_SOON_DISTANCE: 1000,
            TEMPLATE_DUE_SOON_DAYS: 14,
            TEMPLATE_LAST_SERVICE_ODOMETER: 52300,
            TEMPLATE_LAST_SERVICE_DATE: "2026-03-31",
            TEMPLATE_ENABLED: True,
        }
    )

    assert errors == {}
    assert normalized[TEMPLATE_NAME] == "Oil Change"
    assert normalized[TEMPLATE_MILEAGE_INTERVAL] == 10000
    assert normalized[TEMPLATE_TIME_INTERVAL_MONTHS] is None


def test_vehicle_inspection_interval_allows_up_to_999_days() -> None:
    schema = _vehicle_inspection_schema()
    valid = schema(
        {
            "technical_inspection_last_date": "2026-04-01",
            "technical_inspection_interval_days": 999,
        }
    )
    assert valid["technical_inspection_interval_days"] == 999


def test_vehicle_inspection_interval_rejects_values_above_999_days() -> None:
    schema = _vehicle_inspection_schema()
    try:
        schema(
            {
                "technical_inspection_last_date": "2026-04-01",
                "technical_inspection_interval_days": 1000,
            }
        )
    except MultipleInvalid:
        pass
    else:
        raise AssertionError("Expected validation failure for interval > 999")

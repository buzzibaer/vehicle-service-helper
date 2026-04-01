from datetime import date

from custom_components.vehicle_service_helper.reminder_engine import (
    compute_template_status,
    compute_technical_inspection_status,
)


def test_mileage_rule_overdue_when_remaining_distance_is_negative() -> None:
    template = {
        "mileage_interval": 10000,
        "last_service_odometer": 50000,
        "due_soon_distance": 1000,
    }

    result = compute_template_status(
        template=template,
        current_odometer=61050,
        today=date(2026, 3, 31),
    )

    assert result["remaining_distance"] == -1050
    assert result["status"] == "overdue"


def test_time_rule_due_soon_when_inside_threshold() -> None:
    template = {
        "time_interval_months": 6,
        "last_service_date": "2025-10-15",
        "due_soon_days": 14,
    }

    result = compute_template_status(
        template=template,
        current_odometer=20000,
        today=date(2026, 4, 1),
    )

    assert result["remaining_days"] == 14
    assert result["status"] == "due_soon"


def test_both_rules_ok_when_not_close_to_thresholds() -> None:
    template = {
        "mileage_interval": 12000,
        "last_service_odometer": 30000,
        "due_soon_distance": 1500,
        "time_interval_months": 12,
        "last_service_date": "2025-09-01",
        "due_soon_days": 30,
    }

    result = compute_template_status(
        template=template,
        current_odometer=36000,
        today=date(2026, 1, 1),
    )

    assert result["remaining_distance"] == 6000
    assert result["remaining_days"] == 243
    assert result["status"] == "ok"


def test_either_rule_can_trigger_overdue() -> None:
    template = {
        "mileage_interval": 15000,
        "last_service_odometer": 10000,
        "time_interval_months": 12,
        "last_service_date": "2025-03-20",
        "due_soon_days": 30,
    }

    result = compute_template_status(
        template=template,
        current_odometer=12000,
        today=date(2026, 3, 31),
    )

    assert result["remaining_distance"] == 13000
    assert result["remaining_days"] < 0
    assert result["status"] == "overdue"


def test_technical_inspection_next_date_is_calculated_from_last_date_plus_days() -> None:
    result = compute_technical_inspection_status(
        last_inspection_date_iso="2026-01-10",
        interval_days=365,
        today=date(2026, 4, 1),
    )

    assert result["next_inspection_date"] == "2027-01-10"
    assert result["remaining_days"] == 284
    assert result["is_overdue"] is False


def test_technical_inspection_is_overdue_when_next_date_in_past() -> None:
    result = compute_technical_inspection_status(
        last_inspection_date_iso="2024-01-10",
        interval_days=365,
        today=date(2026, 4, 1),
    )

    assert result["next_inspection_date"] == "2025-01-09"
    assert result["remaining_days"] < 0
    assert result["is_overdue"] is True

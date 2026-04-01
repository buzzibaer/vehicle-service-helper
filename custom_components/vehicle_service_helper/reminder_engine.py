from __future__ import annotations

import calendar
from datetime import date, timedelta
from typing import Any

from .const import STATUS_DUE_SOON, STATUS_OK, STATUS_OVERDUE


def _as_positive_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None
    return number if number > 0 else None


def _as_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_iso_date(value: Any) -> date | None:
    if not value or not isinstance(value, str):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _add_months(base: date, months: int) -> date:
    month_index = (base.month - 1) + months
    year = base.year + month_index // 12
    month = (month_index % 12) + 1
    day = min(base.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def compute_technical_inspection_status(
    last_inspection_date_iso: str | None,
    interval_days: int | None,
    today: date,
) -> dict[str, Any]:
    last_inspection_date = _parse_iso_date(last_inspection_date_iso)
    normalized_interval_days = _as_positive_int(interval_days)

    if last_inspection_date is None or normalized_interval_days is None:
        return {
            "next_inspection_date": None,
            "remaining_days": None,
            "is_overdue": False,
            "last_inspection_date": last_inspection_date_iso,
            "interval_days": normalized_interval_days,
        }

    next_inspection_date = last_inspection_date + timedelta(days=normalized_interval_days)
    remaining_days = (next_inspection_date - today).days
    return {
        "next_inspection_date": next_inspection_date.isoformat(),
        "remaining_days": remaining_days,
        "is_overdue": remaining_days < 0,
        "last_inspection_date": last_inspection_date_iso,
        "interval_days": normalized_interval_days,
    }


def compute_template_status(
    template: dict[str, Any],
    current_odometer: float,
    today: date,
) -> dict[str, Any]:
    mileage_interval = _as_positive_int(template.get("mileage_interval"))
    time_interval_months = _as_positive_int(template.get("time_interval_months"))
    due_soon_distance = _as_positive_int(template.get("due_soon_distance")) or 0
    due_soon_days = _as_positive_int(template.get("due_soon_days")) or 0

    remaining_distance: int | None = None
    next_due_odometer: float | None = None

    if mileage_interval is not None:
        last_service_odometer = _as_float(template.get("last_service_odometer"))
        if last_service_odometer is not None:
            next_due_odometer = last_service_odometer + mileage_interval
            remaining_distance = int(round(next_due_odometer - current_odometer))

    remaining_days: int | None = None
    next_due_date_iso: str | None = None

    if time_interval_months is not None:
        last_service_date = _parse_iso_date(template.get("last_service_date"))
        if last_service_date is not None:
            next_due_date = _add_months(last_service_date, time_interval_months)
            remaining_days = (next_due_date - today).days
            next_due_date_iso = next_due_date.isoformat()

    active_remaining_values: list[int] = []
    due_soon_flags: list[bool] = []

    if remaining_distance is not None:
        active_remaining_values.append(remaining_distance)
        due_soon_flags.append(remaining_distance <= due_soon_distance)

    if remaining_days is not None:
        active_remaining_values.append(remaining_days)
        due_soon_flags.append(remaining_days <= due_soon_days)

    status = STATUS_OK
    if active_remaining_values and any(value <= 0 for value in active_remaining_values):
        status = STATUS_OVERDUE
    elif active_remaining_values and any(due_soon_flags):
        status = STATUS_DUE_SOON

    return {
        "status": status,
        "remaining_distance": remaining_distance,
        "remaining_days": remaining_days,
        "next_due_odometer": next_due_odometer,
        "next_due_date": next_due_date_iso,
        "last_service_date": template.get("last_service_date"),
        "last_service_odometer": template.get("last_service_odometer"),
        "is_due": status in {STATUS_DUE_SOON, STATUS_OVERDUE},
    }

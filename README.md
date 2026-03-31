# Vehicle Service Helper

`vehicle_service_helper` is a Home Assistant custom integration for tracking service reminders per vehicle using manual odometer updates and user-defined service templates.

## MVP Features

- One config entry per vehicle
- Empty template list by default (user-defined templates only)
- Template rules based on mileage interval, time interval, or both
- Status calculation: `ok`, `due_soon`, `overdue`
- Manual odometer input with rollback protection
- Services to set odometer and mark service as done

## Entity Model

Per vehicle:

- Number entity for odometer
- Buttons to increase odometer by +100 and +500

Per service template:

- Status sensor
- Remaining distance sensor (if mileage rule enabled)
- Remaining days sensor (if time rule enabled)
- Binary sensor `service_due`

## Services

### `vehicle_service_helper.set_odometer`

- `entry_id` (required)
- `odometer` (required)
- `override` (optional, default `false`)

### `vehicle_service_helper.mark_service_done`

- `entry_id` (required)
- `template_id` (required)
- `service_date` (optional, ISO date)
- `odometer` (optional)

## Notes

- This repository currently lacks a Python runtime in the execution environment, so tests cannot be run here until Python and pytest are available.

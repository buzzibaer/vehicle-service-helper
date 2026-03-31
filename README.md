# Vehicle Service Helper

`vehicle_service_helper` is a Home Assistant custom integration for tracking service reminders per vehicle using manual odometer updates and user-defined service templates.

## MVP Features

- One config entry per vehicle
- Empty template list by default (user-defined templates only)
- Template rules based on mileage interval, time interval, or both
- Status calculation: `ok`, `due_soon`, `overdue`
- Manual odometer input with rollback protection
- Services to set odometer and mark service as done

## Branding

- Repository icon for HACS is provided as `icon.png`.
- Editable source is available as `icon.svg`.
- Integration brand assets are bundled in `custom_components/vehicle_service_helper/` as:
  - `icon.png`, `icon@2x.png`
  - `logo.png`, `logo@2x.png`
- On newer Home Assistant versions (Brands Proxy API), these files are used in the integration UI.
- On older Home Assistant versions, integration tile icons may still require a PR to `home-assistant/brands` under `custom_integrations/vehicle_service_helper/`.

## Installation

You can install this custom integration in two ways.

### Option A: Manual installation (recommended for development)

1. Open your Home Assistant config directory.
2. Create this path if it does not exist: `custom_components/vehicle_service_helper`
3. Copy the contents of this repository folder `custom_components/vehicle_service_helper/` into your Home Assistant config folder at:
   `config/custom_components/vehicle_service_helper/`
4. Restart Home Assistant.
5. Go to **Settings -> Devices & Services -> Add Integration**.
6. Search for **Vehicle Service Helper**.
7. Complete the setup form (vehicle name, distance unit, optional license plate).

### Option B: Install via HACS (custom repository)

If you use HACS, add this repository as a custom integration repo, then install and restart Home Assistant.

Prerequisites:

- HACS is already installed in Home Assistant.
- Advanced mode is enabled for your user profile (needed in some HA versions to see custom repository options).

1. Open HACS.
2. Go to **HACS -> Integrations -> menu (three dots) -> Custom repositories**.
3. Add repository URL:
   `https://github.com/buzzibaer/vehicle-service-helper`
4. Category: **Integration**.
5. Install **Vehicle Service Helper** from HACS.
6. Restart Home Assistant.
7. Add the integration in **Settings -> Devices & Services**.

Updating via HACS:

- When a new version is published, open HACS, update **Vehicle Service Helper**, and restart Home Assistant.

HACS troubleshooting:

- If HACS reports `The version <hash> for this integration can not be used with HACS`, open the repository in HACS and select the latest tagged release version (for example `v0.1.1`) instead of a commit hash.

## Initial Setup in Home Assistant

After adding the integration:

1. Open the integration tile and click **Configure**.
2. Add your first service template (for example Oil Change).
3. Define mileage and/or time intervals.
4. Set baseline values (last service date and odometer).
5. Save.

The integration starts with no templates by default, so reminders appear only after you add templates.

## Entity Model

Per vehicle:

- Number entity for odometer
- Buttons to increase odometer by +100 and +500

Per service template:

- Status sensor
- Remaining distance sensor (if mileage rule enabled)
- Remaining days sensor (if time rule enabled)
- Binary sensor `service_due`

## Typical Usage

- Update odometer in the number entity regularly.
- Use template status sensors in dashboards and automations.
- Use status transitions (`due_soon`, `overdue`) to trigger notifications.

See `docs/automation-examples.md` for YAML examples.

## Services

### `vehicle_service_helper.set_odometer`

- `entry_id` (required)
- `odometer` (required)
- `override` (optional, default `false`)

Example:

```yaml
service: vehicle_service_helper.set_odometer
data:
  entry_id: YOUR_CONFIG_ENTRY_ID
  odometer: 125430
```

### `vehicle_service_helper.mark_service_done`

- `entry_id` (required)
- `template_id` (required)
- `service_date` (optional, ISO date)
- `odometer` (optional)

Example:

```yaml
service: vehicle_service_helper.mark_service_done
data:
  entry_id: YOUR_CONFIG_ENTRY_ID
  template_id: YOUR_TEMPLATE_ID
  service_date: "2026-03-31"
  odometer: 125430
```

## Development

Run tests locally:

```bash
python -m pytest tests -v
```

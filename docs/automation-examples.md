# Automation Examples

These examples use entities created by `vehicle_service_helper`.

## Notify when a service template becomes due soon

```yaml
alias: Vehicle Service Due Soon
trigger:
  - platform: state
    entity_id: sensor.my_car_oil_change_status
    to: due_soon
action:
  - service: notify.mobile_app_phone
    data:
      message: "Oil change is due soon."
mode: single
```

## Notify when a service template becomes overdue

```yaml
alias: Vehicle Service Overdue
trigger:
  - platform: state
    entity_id: sensor.my_car_oil_change_status
    to: overdue
action:
  - service: notify.mobile_app_phone
    data:
      message: "Oil change is overdue."
mode: single
```

## Mark service done from automation

```yaml
alias: Mark Inspection Done
trigger:
  - platform: event
    event_type: custom_vehicle_inspection_complete
action:
  - service: vehicle_service_helper.mark_service_done
    data:
      entry_id: YOUR_CONFIG_ENTRY_ID
      template_id: YOUR_TEMPLATE_ID
mode: single
```

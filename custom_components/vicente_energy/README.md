# Lovelace Card Example

```yaml
type: vertical-stack
cards:
  - type: markdown
    content: |
      ## Vicente Energy Dashboard
      Budget, current power, and session estimates.
  - type: entities
    entities:
      - sensor.charging_budget_24h_kwh
      - sensor.charging_power_level_kw
      - sensor.estimated_session_kwh
      - sensor.estimated_soc_end_pct
      - sensor.estimated_available_after_kwh
  - type: gauge
    entity: sensor.charging_power_level_kw
    min: 0
    max: 10
  - type: entity-button
    name: Reset Learning History
    icon: mdi:restart
    tap_action:
      action: call-service
      service: vicente_energy.reset_history
  - type: entity-button
    name: Set Manual Power
    service: vicente_energy.set_power_level
    service_data:
      power_level_kw: 2.5
```

## Services

- `vicente_energy.set_power_level`  
  Data: `power_level_kw` (float)
- `vicente_energy.reset_history`  
  Clears bias & error history.
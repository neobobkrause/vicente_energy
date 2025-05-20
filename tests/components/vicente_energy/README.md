# Vicente Energy Neighbor Charging Budgeter

## Installation

1. Copy the `vicente_energy` folder into `<config>/custom_components/`.
2. Add to `configuration.yaml`:

   ```yaml
   vicente_energy:
     solar_power_entity: sensor.solar_power
     solar_forecast_entities:
       - sensor.hour_0
       # … through hour_23
     battery_soc_entity: sensor.battery_soc
     house_load_entity: sensor.house_total_load
     wallbox_power_entity: sensor.wallbox_power
     inverter_on_entity: binary_sensor.inverter
     wallbox_state_entity: sensor.charge_state

     # System params
     battery_capacity_kwh: 36.0
     reserve_soc_pct: 20.0
     storage_efficiency: 0.9
     max_charger_power_kw: 7.4
     session_learning_alpha: 0.1

     # Intervals
     budget_update_interval_hours: 1
     update_interval_minutes: 1

sensor:
  - platform: vicente_energy
   ```

## Sensors

- `sensor.charging_budget_24h_kwh` – kWh available next 24h  
- `sensor.charging_power_level_kw` – real-time charging kW  
- `sensor.estimated_soc_end_pct` – projected battery SOC at session end (%)  
- `sensor.estimated_session_kwh` – projected session energy (kWh)  
- `sensor.estimated_available_after_kwh` – kWh left for future charging  
- `sensor.charging_session_kwh_used` – kWh consumed this session  
- `sensor.charging_charge_state` – `unplugged`, `plugged_no_session`, `active_session`, `plugged_post_session`

## Development

- Run unit tests:  
  ```bash
  pytest -q
  ```
- Integration test script:  
  ```bash
  python integration_test.py
  ```
- Config flow UI will be available after restart in Integrations.
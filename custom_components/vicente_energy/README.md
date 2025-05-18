# Vicente Energy Home Assistant Integration

Vicente Energy intelligently automates solar PV, battery storage, and electric vehicle charging by dynamically optimizing energy flows based on solar forecasts and real-time energy use.

## Project Structure

- **`custom_components/vicente_energy/`**  
  Contains the Home Assistant integration itself. Install into your HA instance by placing under your `custom_components/` folder.

- **`tests/`**  
  Comprehensive tests written using pytest, directly validating integration components.

## Installation into Home Assistant

To install, copy the `custom_components/vicente_energy` folder into your Home Assistant folder:

home-assistant-core
└─── custom_components/
     └─── vicente_energy/ # VE souce files here
└─── tests/
     └─── components/ # VE test files here
          └─── vicente_enegy/ # VE test files here


Restart Home Assistant after placing the files.

## Testing Instructions

Run your tests using pytest from the home-assistant-core root:

pytest tests/

## Configuration

Use the UI to configure via **Settings > Devices & Services > Add Integration** and select **Vicente Energy**. Provide:
- EV charger integration service choice
- Battery integration service choice
- Solar integration service choice
- Grid integration service choice
- Solar forecasting integration service choice
- Location name
- Battery capacity in kWh
- Battery SOC reserve percentage
- Estimated battery storage round trip efficiency

## Core Modules

- **charge_estimator.py**: Manages EV charging forecasts and dynamic charging levels.
- **state_manager.py**: Centralized state management.
- **solar_adapter.py**: Interfaces with solar data providers.
- **forecast_accuracy_tracker.py**: Tracks forecasting accuracy for continuous improvement.
- **load_forecaster.py**: Predicts home energy loads dynamically.
- **session_manager.py**: Manages sessions, learning state, and persistent data storage.
- **sensor_entities.py**: Defines Home Assistant sensor entities.
- **input_collector.py**: Gathers real-time data inputs from sensors/services.

## Available Services

Vicente Energy explicitly provides the following integrations and services:

### Battery Integration Services:
- **Franklin Battery Service** (`franklin_service.py`)
- Generic battery service interface (`battery_service.py`)

### EV Charger Integration Services:
- **Wallbox EV Charger Service** (`wallbox_service.py`)
- Generic EV charger interface (`ev_charger_service.py`)

### Solar Integration Services:
- **Solcast Forecast Service** (`solcast_service.py`)
- Generic solar service interface (`solar_service.py`)

### Forecasting Services:
- Generic forecast interface (`forecast_service.py`)

## Services

- `vicente_energy.set_power_level`
- `vicente_energy.reset_history`

For details, see [documentation](https://github.com/yourrepo/vicente_energy).

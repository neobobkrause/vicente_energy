from custom_components.vicente_energy import DOMAIN
from custom_components.vicente_energy.charge_estimator import ChargeEstimator, Forecasts
from custom_components.vicente_energy.forecast_accuracy_tracker import (
    ForecastAccuracyTracker,
)
from custom_components.vicente_energy.input_collector import InputCollector
from custom_components.vicente_energy.load_forecaster import LoadForecaster
from custom_components.vicente_energy.solar_adapter import SolarForecastAdapter
from custom_components.vicente_energy.state_manager import StateManager
import pytest


@pytest.mark.asyncio
async def test_hourly_simulation(hass):
    config = {
        DOMAIN: {
            "solar_power_entity": "sensor.solar_power",
            "solar_forecast_entities": [f"sensor.hour_{i}" for i in range(24)],
            "battery_soc_entity": "sensor.battery_soc",
            "house_load_entity": "sensor.house_load",
            "wallbox_power_entity": "sensor.wallbox_power",
            "inverter_on_entity": "binary_sensor.inverter",
            "wallbox_state_entity": "sensor.charge_state",
        }
    }

    state_manager = StateManager(hass, entry_id="test")
    await state_manager.async_load()
    collector = InputCollector(
        hass,
        "sensor.solar_power",
        "sensor.battery_soc",
        "sensor.house_load",
        "sensor.wallbox_power",
        "binary_sensor.inverter",
    )
    solar = SolarForecastAdapter(
        hass, config[DOMAIN]["solar_forecast_entities"], state_manager
    )
    load = LoadForecaster(hass, config[DOMAIN], state_manager)
    tracker = ForecastAccuracyTracker(state_manager, alpha=0.1)
    estimator = ChargeEstimator(config[DOMAIN], state_manager)

    # Set initial states explicitly
    hass.states.async_set("sensor.solar_power", "5000")
    hass.states.async_set("sensor.house_load", "3000")
    hass.states.async_set("sensor.wallbox_power", "0")
    hass.states.async_set("sensor.battery_soc", "50")
    hass.states.async_set("binary_sensor.inverter", "on")

    await hass.async_block_till_done()

    # Simulate hourly update
    signals = collector.get_signals()
    solar_fc = await solar.get_corrected_forecast()
    load_fc = load.get_corrected_forecast()
    budget = estimator.compute_24h_budget(Forecasts(solar_fc, load_fc), signals)

    assert budget is not None
    print(f"Simulated budget: {budget}")

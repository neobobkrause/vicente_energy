from custom_components.vicente_energy.charge_estimator import ChargeEstimator
from custom_components.vicente_energy.input_collector import InputCollector
from custom_components.vicente_energy.state_manager import StateManager
import pytest

from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component


@pytest.mark.asyncio
async def test_day_in_life(hass: HomeAssistant):
    config = {
        "vicente_energy": {
            "solar_power_entity": "sensor.solar",
            "solar_forecast_entities": ["sensor.f1"],
            "battery_soc_entity": "sensor.soc",
            "house_load_entity": "sensor.load",
            "wallbox_power_entity": "sensor.wp",
            "inverter_on_entity": "binary_sensor.inv",
            "wallbox_state_entity": "sensor.state",
        }
    }
    await async_setup_component(hass, "vicente_energy", config)
    await hass.async_block_till_done()

    hass.states.async_set("sensor.solar", "5000")
    hass.states.async_set("sensor.soc", "50")
    hass.states.async_set("sensor.load", "3000")
    hass.states.async_set("sensor.wp", "0")
    hass.states.async_set("binary_sensor.inv", "on")
    hass.states.async_set("sensor.state", "idle")

    await hass.async_block_till_done()

    sm = StateManager(hass, entry_id="test")
    signals = InputCollector(
        hass,
        "sensor.solar",
        "sensor.soc",
        "sensor.load",
        "sensor.wp",
        "binary_sensor.inv",
        "sensor.state",
    ).get_signals()

    ce = ChargeEstimator(
        {
            "battery_capacity_kwh": 5,
            "reserve_soc_pct": 20,
            "storage_efficiency": 0.9,
            "max_charger_power_kw": 3,
            "session_learning_alpha": 0.1,
        },
        sm,
    )

    forecasts = type("F", (), {"solar_24h_kwh": [1] * 24, "load_24h_kwh": [0] * 24})
    budget = ce.compute_24h_budget(forecasts, signals)
    assert budget >= 0

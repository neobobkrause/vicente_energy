import asyncio
from custom_components.vicente_energy import DOMAIN
from custom_components.vicente_energy.charge_estimator import ChargeEstimator, Forecasts
from custom_components.vicente_energy.input_collector import InputCollector
from custom_components.vicente_energy.state_manager import StateManager
from custom_components.vicente_energy.solar_adapter import SolarForecastAdapter
from custom_components.vicente_energy.load_forecaster import LoadForecaster
from custom_components.vicente_energy.forecast_accuracy_tracker import ForecastAccuracyTracker

class DummyHass(dict):
    def __init__(self):
        super().__init__()
        self.states = {}
    def async_create_task(self, coro): pass

    @property
    def states_get(self):
        return self.states

# Simulate one hourly tick
async def main():
    hass = DummyHass()
    # stub state and config
    config = {
        DOMAIN: {
            'solar_power_entity':'sensor.solar_power',
            'solar_forecast_entities':[f'sensor.hour_{i}' for i in range(24)],
            'battery_soc_entity':'sensor.battery_soc',
            'house_load_entity':'sensor.house_load',
            'wallbox_power_entity':'sensor.wallbox_power',
            'inverter_on_entity':'binary_sensor.inverter',
            'wallbox_state_entity':'sensor.charge_state',
        }
    }
    state_manager = StateManager(hass)
    await state_manager.async_load()
    collector = InputCollector(
        hass,
        'sensor.solar_power',
        'sensor.battery_soc',
        'sensor.house_load',
        'sensor.wallbox_power',
        'binary_sensor.inverter'
    )
    solar = SolarForecastAdapter(hass, config[DOMAIN]['solar_forecast_entities'], state_manager)
    load = LoadForecaster(state_manager)
    tracker = ForecastAccuracyTracker(state_manager)
    estimator = ChargeEstimator(config[DOMAIN], state_manager)

    # initialize with some dummy states
    hass.states={'sensor.solar_power': type('S', (), {'state':'5000'}),
                'sensor.house_load':'3000',
                'sensor.wallbox_power':'0',
                'sensor.battery_soc':'50',
                'binary_sensor.inverter':'on'}
    # Simulate hourly update
    signals = collector.get_signals()
    solar_fc = solar.get_corrected_forecast()
    load_fc = load.get_corrected_forecast()
    budget = estimator.compute_24h_budget(Forecasts(solar_fc, load_fc), signals)
    print(f"Simulated budget: {budget}")

if __name__ == '__main__':
    asyncio.run(main())
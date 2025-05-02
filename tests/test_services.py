import pytest

from custom_components.vicente_energy.state_manager import StateManager
from custom_components.vicente_energy import DOMAIN

class DummyServices:
    def __init__(self):
        self._services = {}

    def async_register(self, domain, service, handler):
        # Synchronously register the handler
        self._services.setdefault(domain, {})[service] = handler

class DummyHass:
    def __init__(self):
        self.data = {}
        self.services = DummyServices()

@pytest.fixture
def hass():
    hass = DummyHass()
    # Initialize data store with a StateManager
    hass.data[DOMAIN] = {'state_manager': StateManager(hass)}
    return hass

@pytest.mark.asyncio
async def test_set_power_level_service(hass):
    from custom_components.vicente_energy import async_setup
    DV = DOMAIN
    # Setup integration, which calls async_register
    await async_setup(hass, {DV: {
        "solar_power_entity": "", "solar_forecast_entities": [],
        "battery_soc_entity": "", "house_load_entity": "",
        "wallbox_power_entity": "", "inverter_on_entity": "",
        "wallbox_state_entity": ""
    }})
    # Verify service handler is registered by integration
    assert 'set_power_level' in hass.services._services[DV]
    handler = hass.services._services[DV]['set_power_level']
    # Invoke the handler (async def)
    await handler({'power_level_kw': 2.5})
    assert hass.data[DV].get('manual_power_level') == 2.5

@pytest.mark.asyncio
async def test_reset_history_service(hass):
    from custom_components.vicente_energy import async_setup
    DV = DOMAIN
    manager = hass.data[DV]['state_manager']
    # Pre-populate history
    manager.data['session_bias_history'] = [0.1, 0.2]
    manager.data['forecast_error_history'] = {'solar_errors': [0.05], 'load_errors': [0.1]}
    manager.data['last_raw_session_kwh'] = 4.2

    # Setup integration, which registers reset_history
    await async_setup(hass, {DV: {
        "solar_power_entity": "", "solar_forecast_entities": [],
        "battery_soc_entity": "", "house_load_entity": "",
        "wallbox_power_entity": "", "inverter_on_entity": "",
        "wallbox_state_entity": ""
    }})
    # Verify reset_history service
    assert 'reset_history' in hass.services._services[DV]
    handler = hass.services._services[DV]['reset_history']
    # Invoke handler
    await handler({})
    assert manager.data['session_bias_history'] == []
    assert manager.data['forecast_error_history'] == {'solar_errors': [], 'load_errors': []}
    assert manager.data['last_raw_session_kwh'] is None
import pytest
from homeassistant import config_entries
from custom_components.vicente_energy.config_flow import VicenteFlowHandler

class DummyHass:
    def __init__(self):
        self.async_create_task = lambda x: None

@pytest.fixture
def hass():
    hass = DummyHass()
    hass.config_entries = config_entries
    return hass

@pytest.mark.asyncio
async def test_step_user_form(hass):
    flow = VicenteFlowHandler()
    result = await flow.async_step_user()
    assert result['type'] == 'form'
    assert 'data_schema' in result

@pytest.mark.asyncio
async def test_step_user_create_entry(hass):
    flow = VicenteFlowHandler()
    user_input = {
        "solar_power_entity": "sensor.solar",
        "solar_forecast_entities": ["sensor.forecast"],
        "battery_soc_entity": "sensor.soc",
        "house_load_entity": "sensor.load",
        "wallbox_power_entity": "sensor.wp",
        "inverter_on_entity": "binary_sensor.inv",
        "wallbox_state_entity": "sensor.state",
        "battery_capacity_kwh": 20.0,
        "reserve_soc_pct": 25.0,
        "storage_efficiency": 0.95,
        "max_charger_power_kw": 7.4,
        "session_learning_alpha": 0.1,
        "budget_update_interval_hours": 2,
        "update_interval_minutes": 5,
    }
    result = await flow.async_step_user(user_input)
    assert result['type'] == 'create_entry'
    assert result['data'] == user_input
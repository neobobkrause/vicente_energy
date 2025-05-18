from custom_components.vicente_energy.solar_adapter import SolarForecastAdapter
from custom_components.vicente_energy.state_manager import StateManager
import pytest

from homeassistant.core import HomeAssistant


@pytest.fixture
async def state_manager(hass: HomeAssistant):
    sm = StateManager(hass, entry_id="test")
    await sm.async_load()
    return sm


@pytest.fixture
async def setup_sensors(hass: HomeAssistant):
    for i in range(24):
        hass.states.async_set(f"sensor.s{i}", "0")
    await hass.async_block_till_done()


@pytest.mark.asyncio
async def test_nonstandard_length_and_zero_division(
    hass: HomeAssistant, state_manager, setup_sensors
):
    sensors = [f"sensor.s{i}" for i in range(24)]
    adapter = SolarForecastAdapter(hass, sensors, state_manager)
    raw = await adapter.get_raw_forecast()
    assert len(raw) == 24

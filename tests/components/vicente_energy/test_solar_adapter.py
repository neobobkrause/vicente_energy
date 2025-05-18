from unittest.mock import MagicMock

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
    for i in range(48):
        hass.states.async_set(f"sensor.fc_{i}", str(i))
    await hass.async_block_till_done()


@pytest.mark.asyncio
async def test_get_raw_forecast_halfhour(
    hass: HomeAssistant, state_manager, setup_sensors
):
    sensors = [f"sensor.fc_{i}" for i in range(48)]
    adapter = SolarForecastAdapter(hass, sensors, state_manager)
    raw = await adapter.get_raw_forecast()
    assert len(raw) == 48
    assert raw[0] == 0.0
    assert raw[-1] == 47.0


@pytest.mark.asyncio
async def test_corrected_forecast_applies_bias(
    hass: HomeAssistant, state_manager, setup_sensors
):
    state_manager.update_solar_bias(0.5)
    sensors = [f"sensor.fc_{i}" for i in range(48)]
    adapter = SolarForecastAdapter(hass, sensors, state_manager)
    corrected = await adapter.get_corrected_forecast()
    assert corrected[0] == 0.0


@pytest.mark.asyncio
async def test_adapter_uses_forecast_service_if_available(hass: HomeAssistant):
    service_mock = MagicMock()
    from unittest.mock import AsyncMock

    service_mock.get_forecast = AsyncMock(return_value={"values": [100.0] * 48})
    manager = MagicMock()
    manager.get_forecast = service_mock.get_forecast
    adapter = SolarForecastAdapter(hass, [], MagicMock(), service_manager=manager)
    result = await adapter.get_raw_forecast()
    assert isinstance(result, list)
    assert result[0] == 100.0

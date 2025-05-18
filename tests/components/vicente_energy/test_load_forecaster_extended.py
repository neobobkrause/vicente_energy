from custom_components.vicente_energy.load_forecaster import LoadForecaster
from custom_components.vicente_energy.state_manager import StateManager
import pytest

from homeassistant.core import HomeAssistant


@pytest.fixture
async def state_manager(hass: HomeAssistant):
    sm = StateManager(hass, entry_id="test")
    await sm.async_load()
    return sm


@pytest.fixture
def forecaster(hass: HomeAssistant, state_manager):
    return LoadForecaster(hass=hass, config={}, state_manager=state_manager)


def test_no_history_returns_zeros(forecaster):
    corrected = forecaster.get_corrected_forecast()
    assert isinstance(corrected, list)
    assert all(v == 0.0 for v in corrected)


def test_bias_applied_to_load_forecast(forecaster, state_manager):
    for v in [1.0, 2.0, 3.0]:
        forecaster.update_history(v)
    state_manager.update_load_bias(0.2)  # +20%
    raw = forecaster.get_raw_forecast()
    corrected = forecaster.get_corrected_forecast()
    assert len(raw) == len(corrected)
    for r, c in zip(raw, corrected):
        assert c == pytest.approx(r * 1.2)

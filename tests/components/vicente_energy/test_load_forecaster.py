from custom_components.vicente_energy.load_forecaster import LoadForecaster
from custom_components.vicente_energy.state_manager import StateManager
import pytest

from homeassistant.core import HomeAssistant


@pytest.fixture
async def state_manager(hass: HomeAssistant):
    sm = StateManager(hass, entry_id="test_entry")
    await sm.async_load()
    return sm


@pytest.fixture
def forecaster(hass: HomeAssistant, state_manager):
    return LoadForecaster(hass=hass, config={}, state_manager=state_manager)


def test_load_forecast_padding(forecaster):
    fc = forecaster.get_corrected_forecast()
    assert len(fc) == 24
    assert all(v == 0.0 for v in fc)


def test_load_forecast_bias(forecaster, state_manager):
    for v in [1.0, 2.0, 3.0]:
        forecaster.update_history(v)
    state_manager.update_load_bias(0.5)
    fc = forecaster.get_corrected_forecast()
    assert pytest.approx(fc[-3:], rel=1e-3) == [1.5, 3.0, 4.5]


def test_raw_forecast_length(forecaster):
    raw = forecaster.get_raw_forecast()
    assert len(raw) == 24


def test_bias_application_load(forecaster, state_manager):
    state_manager.update_load_bias(0.2)
    raw = forecaster.get_raw_forecast()
    corrected = forecaster.get_corrected_forecast()
    for r, c in zip(raw, corrected):
        assert c == pytest.approx(r * 1.2)

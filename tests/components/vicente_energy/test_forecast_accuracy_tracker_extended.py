from custom_components.vicente_energy.forecast_accuracy_tracker import (
    ForecastAccuracyTracker,
)
from custom_components.vicente_energy.state_manager import StateManager
import pytest

from homeassistant.core import HomeAssistant


@pytest.fixture
async def state_manager(hass: HomeAssistant):
    sm = StateManager(hass, entry_id="test")
    await sm.async_load()
    return sm


@pytest.fixture
def tracker(state_manager):
    return ForecastAccuracyTracker(state_manager, alpha=0.2)


def test_update_solar_bias(tracker, state_manager):
    tracker.update_solar(10, 12)
    bias = state_manager.get_solar_bias()
    assert bias != 0.0


def test_update_load_bias(tracker, state_manager):
    tracker.update_load(5, 2)
    bias = state_manager.get_load_bias()
    assert bias != 0.0


def test_zero_forecast_skipped(tracker, state_manager):
    state_manager.update_solar_bias(0.1)
    tracker.update_solar(0, 5)
    assert state_manager.get_solar_bias() == pytest.approx(0.1)

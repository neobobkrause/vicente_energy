from custom_components.vicente_energy.forecast_accuracy_tracker import (
    ForecastAccuracyTracker,
)
from custom_components.vicente_energy.state_manager import StateManager
import pytest

from homeassistant.core import HomeAssistant


@pytest.fixture
async def state_manager(hass: HomeAssistant):
    sm = StateManager(hass, entry_id="test_entry")
    await sm.async_load()
    return sm


@pytest.fixture
def tracker(state_manager):
    return ForecastAccuracyTracker(state_manager, alpha=0.2)


def test_solar_bias_update(tracker, state_manager):
    tracker.update_solar(10, 12)
    assert pytest.approx(state_manager.get_solar_bias(), rel=1e-3) == 0.04


def test_load_bias_update(tracker, state_manager):
    tracker.update_load(5, 2)
    assert pytest.approx(state_manager.get_load_bias(), rel=1e-3) == -0.12

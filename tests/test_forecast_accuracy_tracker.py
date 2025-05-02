import pytest
from custom_components.vicente_energy.forecast_accuracy_tracker import ForecastAccuracyTracker
from custom_components.vicente_energy.state_manager import StateManager

class DummyHass: pass

@pytest.fixture
def state_manager():
    return StateManager(DummyHass())

@pytest.fixture
def tracker(state_manager):
    return ForecastAccuracyTracker(state_manager, alpha=0.2)

def test_solar_bias_update(tracker, state_manager):
    # forecast 10, actual 12 -> error=(12-10)/10=0.2 -> new_bias=0.2*0.2=0.04
    tracker.update_solar(10, 12)
    assert pytest.approx(state_manager.get_solar_bias(), rel=1e-3) == 0.04

def test_load_bias_update(tracker, state_manager):
    # forecast 5, actual 2 -> error=(2-5)/5=-0.6 -> new_bias=-0.6*0.2=-0.12
    tracker.update_load(5, 2)
    assert pytest.approx(state_manager.get_load_bias(), rel=1e-3) == -0.12
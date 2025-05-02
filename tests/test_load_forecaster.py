import pytest
from custom_components.vicente_energy.load_forecaster import LoadForecaster
from custom_components.vicente_energy.state_manager import StateManager

class DummyHass: pass

@pytest.fixture
def state_manager():
    return StateManager(DummyHass())

@pytest.fixture
def forecaster(state_manager):
    return LoadForecaster(state_manager)

def test_load_forecast_padding(forecaster):
    # no history -> all zeros
    fc = forecaster.get_corrected_forecast()
    assert len(fc) == 24
    assert all(v == 0.0 for v in fc)

def test_load_forecast_bias(forecaster, state_manager):
    # add history and bias
    for v in [1.0, 2.0, 3.0]:
        forecaster.update_history(v)
    state_manager.update_load_bias(0.5)  # +50%
    fc = forecaster.get_corrected_forecast()
    # first 21 zeros, then 1.5,3.0,4.5
    assert pytest.approx(fc[-3:], rel=1e-3) == [1.5, 3.0, 4.5]
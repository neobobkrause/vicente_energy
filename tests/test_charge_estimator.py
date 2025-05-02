import pytest
from custom_components.vicente_energy.charge_estimator import ChargeEstimator
from custom_components.vicente_energy.models import Signals, Forecasts, SessionActuals
from custom_components.vicente_energy.state_manager import StateManager

class DummyHass:
    pass

@pytest.fixture
def state_manager():
    # Create a dummy Home Assistant object for StateManager
    hass = DummyHass()
    sm = StateManager(hass)
    # No async_load called here; biases will default to 0
    return sm

@pytest.fixture
def estimator(state_manager):
    params = {
        "battery_capacity_kwh": 10.0,
        "reserve_soc_pct": 20.0,
        "storage_efficiency": 0.9,
        "max_charger_power_kw": 5.0,
        "session_learning_alpha": 0.1
    }
    return ChargeEstimator(params, state_manager)

def test_compute_24h_budget_simple(estimator):
    # Forecast: 10 kWh solar, 2 kWh load
    fc = Forecasts(solar_24h_kwh=[0]*23 + [10], load_24h_kwh=[0]*23 + [2])
    # Battery SOC at 50%; reserve at 20%
    sig = Signals(solar_power_w=0, battery_soc_pct=50, house_load_total_w=0, wallbox_power_w=0, agate_inverter_on=True)
    budget = estimator.compute_24h_budget(fc, sig)
    # total_solar=10, total_load=2, battery_avail=(0.5-0.2)*10*0.9=2.7 => budget=10-2+2.7=10.7
    assert pytest.approx(budget, rel=1e-3) == 10.7

def test_compute_power_level_solar(estimator):
    # Enough solar to cover load + 3 kW spare
    sig = Signals(solar_power_w=6000, battery_soc_pct=50, house_load_total_w=3000, wallbox_power_w=0, agate_inverter_on=True)
    power = estimator.compute_power_level(sig, budget_remaining=5.0)
    # direct = (6-3)=3 kW; max_power=5 -> expect 3
    assert pytest.approx(power, rel=1e-3) == 3.0

def test_compute_power_level_battery(estimator):
    # No solar, battery at 80% SOC, reserve 20% => soc_above=0.6 => available=0.6*10*0.9=5.4 kWh
    sig = Signals(solar_power_w=0, battery_soc_pct=80, house_load_total_w=0, wallbox_power_w=0, agate_inverter_on=True)
    power = estimator.compute_power_level(sig, budget_remaining=10.0)
    # battery draw scenario: batt_kwh=5.4 => batt_kw=5.4; max_power=5 => expect 5
    assert pytest.approx(power, rel=1e-3) == 5.0

def test_session_learning(estimator, state_manager):
    # Simulate a session where actual kWh > estimate, check bias update
    # Initial bias = 0
    actual = SessionActuals(kwh_used=2.0)
    estimator.learn_session(actual)
    # After learning, bias should update (not zero)
    assert state_manager.get_session_bias() != 0.0
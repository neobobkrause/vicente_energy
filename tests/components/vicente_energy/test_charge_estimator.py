from custom_components.vicente_energy.charge_estimator import ChargeEstimator
from custom_components.vicente_energy.const import (
    CONF_BATTERY_CAPACITY_KWH,
    CONF_MAX_CHARGER_POWER_KW,
    CONF_RESERVE_SOC_PCT,
    CONF_SESSION_LEARNING_ALPHA,
    CONF_STORAGE_EFFICIENCY,
)
from custom_components.vicente_energy.models import Forecasts, SessionActuals, Signals
from custom_components.vicente_energy.state_manager import StateManager
import pytest

from homeassistant.core import HomeAssistant


@pytest.fixture
async def state_manager(hass: HomeAssistant):
    sm = StateManager(hass, entry_id="test")
    await sm.async_load()
    return sm


@pytest.fixture
async def estimator(state_manager):
    params = {
        CONF_BATTERY_CAPACITY_KWH: 10.0,
        CONF_RESERVE_SOC_PCT: 20.0,
        CONF_STORAGE_EFFICIENCY: 0.9,
        CONF_MAX_CHARGER_POWER_KW: 5.0,
        CONF_SESSION_LEARNING_ALPHA: 0.1,
    }
    return ChargeEstimator(params, state_manager)


def test_compute_24h_budget_simple(estimator):
    fc = Forecasts(solar_24h_kwh=[0] * 23 + [10], load_24h_kwh=[0] * 23 + [2])
    sig = Signals(
        solar_power_w=0,
        battery_soc_pct=50,
        house_load_total_w=0,
        wallbox_power_w=0,
        agate_inverter_on=True,
    )
    budget = estimator.compute_24h_budget(fc, sig)
    assert pytest.approx(budget, rel=1e-3) == 10.7


def test_compute_power_level_solar(estimator):
    sig = Signals(
        solar_power_w=6000,
        battery_soc_pct=50,
        house_load_total_w=3000,
        wallbox_power_w=0,
        agate_inverter_on=True,
    )
    power = estimator.compute_power_level(sig, budget_remaining=5.0)
    assert pytest.approx(power, rel=1e-3) == 3.0


def test_compute_power_level_battery(estimator):
    sig = Signals(
        solar_power_w=0,
        battery_soc_pct=80,
        house_load_total_w=0,
        wallbox_power_w=0,
        agate_inverter_on=True,
    )
    power = estimator.compute_power_level(sig, budget_remaining=10.0)
    assert pytest.approx(power, rel=1e-3) == 5.0


@pytest.mark.asyncio
async def test_session_learning(estimator, state_manager):
    actual = SessionActuals(kwh_used=2.0)
    await estimator.learn_session(actual)
    assert state_manager.get_session_bias() != 0.0


def test_power_level_inverter_off(estimator):
    sig = Signals(
        solar_power_w=1000,
        battery_soc_pct=50,
        house_load_total_w=0,
        wallbox_power_w=0,
        agate_inverter_on=False,
    )
    power = estimator.compute_power_level(sig, budget_remaining=10)
    assert power == 0

from custom_components.vicente_energy.charge_estimator import ChargeEstimator
from custom_components.vicente_energy.const import (
    CONF_BATTERY_CAPACITY_KWH,
    CONF_MAX_CHARGER_POWER_KW,
    CONF_RESERVE_SOC_PCT,
    CONF_SESSION_LEARNING_ALPHA,
    CONF_STORAGE_EFFICIENCY,
)
from custom_components.vicente_energy.models import Forecasts, Signals
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


def test_reserve_enforcement(estimator):
    sig = Signals(
        solar_power_w=0,
        battery_soc_pct=20.0,
        house_load_total_w=0,
        wallbox_power_w=0,
        agate_inverter_on=True,
    )
    power = estimator.compute_power_level(sig, budget_remaining=10.0)
    assert power == 0.0


def test_full_battery_zero_budget(estimator):
    fc = Forecasts(solar_24h_kwh=[0] * 24, load_24h_kwh=[0] * 24)
    sig = Signals(
        solar_power_w=0,
        battery_soc_pct=100.0,
        house_load_total_w=0,
        wallbox_power_w=0,
        agate_inverter_on=True,
    )
    budget = estimator.compute_24h_budget(fc, sig)
    assert budget == pytest.approx(0.0)

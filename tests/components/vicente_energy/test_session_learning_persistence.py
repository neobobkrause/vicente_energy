from custom_components.vicente_energy.charge_estimator import ChargeEstimator
from custom_components.vicente_energy.const import (
    CONF_BATTERY_CAPACITY_KWH,
    CONF_MAX_CHARGER_POWER_KW,
    CONF_RESERVE_SOC_PCT,
    CONF_SESSION_LEARNING_ALPHA,
    CONF_STORAGE_EFFICIENCY,
)
from custom_components.vicente_energy.models import SessionActuals
from custom_components.vicente_energy.state_manager import StateManager
import pytest

from homeassistant.core import HomeAssistant


@pytest.fixture
async def state_manager(hass: HomeAssistant):
    sm = StateManager(hass, entry_id="test")
    await sm.async_load()
    return sm


@pytest.mark.asyncio
async def test_multiple_session_learning(state_manager):
    params = {
        CONF_BATTERY_CAPACITY_KWH: 10.0,
        CONF_RESERVE_SOC_PCT: 20.0,
        CONF_STORAGE_EFFICIENCY: 0.9,
        CONF_MAX_CHARGER_POWER_KW: 5.0,
        CONF_SESSION_LEARNING_ALPHA: 0.1,
    }
    estimator = ChargeEstimator(params, state_manager)
    await estimator.learn_session(SessionActuals(kwh_used=2.0))
    bias1 = state_manager.get_session_bias()
    await estimator.learn_session(SessionActuals(kwh_used=3.0))
    bias2 = state_manager.get_session_bias()
    assert bias2 != bias1

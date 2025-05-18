from custom_components.vicente_energy.state_manager import StateManager
import pytest

from homeassistant.core import HomeAssistant


@pytest.fixture
async def state_manager(hass: HomeAssistant):
    sm = StateManager(hass, entry_id="test_entry")
    await sm.async_load()
    return sm


def test_initial_state(state_manager):
    d = state_manager.data
    assert d["solar_bias"] == 0.0
    assert d["load_bias"] == 0.0
    assert d["session_bias"] == 0.0
    assert d["forecast_error_history"] == {"solar_errors": [], "load_errors": []}
    assert d["session_bias_history"] == []
    assert d["last_raw_session_kwh"] is None


@pytest.mark.asyncio
async def test_update_session_bias_incremental(state_manager):
    await state_manager.update_session_bias(0.5, actual_kwh=2.0)
    assert state_manager.get_session_bias() == 1.0

    await state_manager.update_session_bias(0.5, actual_kwh=3.0)
    assert state_manager.get_session_bias() == 2.0


@pytest.mark.asyncio
async def test_set_session_bias_direct(state_manager):
    await state_manager.set_session_bias(0.8)
    assert state_manager.get_session_bias() == 0.8

    await state_manager.set_session_bias(-0.2)
    assert state_manager.get_session_bias() == -0.2


@pytest.mark.asyncio
async def test_reset_history(state_manager):
    state_manager.update_solar_bias(1)
    state_manager.record_forecast_error("solar", 0.1)
    await state_manager.update_session_bias(0.8, actual_kwh=2.0)
    await state_manager.reset_history()
    assert state_manager.data["solar_bias"] == 0.0
    assert state_manager.data["load_bias"] == 0.0
    assert state_manager.data["session_bias"] == 0.0
    assert state_manager.data["forecast_error_history"] == {
        "solar_errors": [],
        "load_errors": [],
    }
    assert state_manager.data["session_bias_history"] == []
    assert state_manager.data["last_raw_session_kwh"] is None

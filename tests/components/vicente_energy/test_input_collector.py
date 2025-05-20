from unittest.mock import MagicMock

from custom_components.vicente_energy.input_collector import InputCollector
import pytest

from homeassistant.core import HomeAssistant


@pytest.fixture
async def setup_states(hass: HomeAssistant):
    hass.states.async_set("sensor.solar", "100.5")
    hass.states.async_set("sensor.soc", "75")
    hass.states.async_set("sensor.load", "250")
    hass.states.async_set("sensor.wp", "50")
    hass.states.async_set("binary_sensor.inv", "on")
    await hass.async_block_till_done()


def test_get_signals_defaults(hass: HomeAssistant):
    collector = InputCollector(
        hass, "unknown", "unknown", "unknown", "unknown", "unknown"
    )
    signals = collector.get_signals()
    assert signals.solar_power_w == 0.0
    assert signals.battery_soc_pct == 0.0
    assert signals.house_load_total_w == 0.0
    assert signals.wallbox_power_w == 0.0
    assert signals.agate_inverter_on is False


@pytest.mark.usefixtures("setup_states")
def test_get_signals_parsing(hass: HomeAssistant):
    collector = InputCollector(
        hass,
        "sensor.solar",
        "sensor.soc",
        "sensor.load",
        "sensor.wp",
        "binary_sensor.inv",
    )
    signals = collector.get_signals()
    assert signals.solar_power_w == pytest.approx(100.5)
    assert signals.battery_soc_pct == 75.0
    assert signals.house_load_total_w == 250.0
    assert signals.wallbox_power_w == 50.0
    assert signals.agate_inverter_on is True


@pytest.mark.asyncio
async def test_input_collector_prefers_service_charger_data(hass: HomeAssistant):
    # Set up mock charger service with expected return value
    manager = MagicMock()
    manager.get_charger_state = MagicMock(return_value={"charging_power": 8.0})

    # Use known-good dummy entity names
    collector = InputCollector(
        hass,
        "sensor.fake_solar",
        "sensor.fake_soc",
        "sensor.fake_load",
        "sensor.fake_wp",
        "binary_sensor.fake_inv",
        "sensor.fake_state",
        service_manager=manager,
    )

    # This forces InputCollector to skip entity and use manager
    collector._wallbox_power_entity = None

    result = collector.get_signals()

    assert abs(result.wallbox_power_w - 8.0) < 0.01

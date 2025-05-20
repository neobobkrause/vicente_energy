from custom_components.vicente_energy.input_collector import InputCollector
from custom_components.vicente_energy.models import Signals
import pytest

from homeassistant.core import HomeAssistant


@pytest.fixture
def collector(hass: HomeAssistant):
    # Entities explicitly missing; no state set
    return InputCollector(
        hass,
        solar_power_entity="sensor.solar",
        solar_forecast_entities=[],
        battery_soc_entity="sensor.soc",
        house_load_entity="sensor.load",
        wallbox_power_entity="sensor.wp",
        inverter_on_entity="binary_sensor.inv",
        wallbox_state_entity="sensor.state",
    )


def test_missing_values_default_zero(collector):
    signals: Signals = collector.get_signals()
    assert signals.solar_power_w == 0.0
    assert signals.battery_soc_pct == 0.0
    assert signals.house_load_total_w == 0.0
    assert signals.wallbox_power_w == 0.0
    assert signals.agate_inverter_on is False

from custom_components.vicente_energy.input_collector import InputCollector

from homeassistant.core import HomeAssistant


def test_missing_entities_defaults(hass: HomeAssistant):
    collector = InputCollector(
        hass,
        solar_entity="sensor.missing",
        battery_entity="sensor.missing2",
        load_entity="sensor.missing3",
        wallbox_power_entity="sensor.missing4",
        inverter_on_entity="binary_sensor.missing5",
    )
    signals = collector.get_signals()
    assert signals.solar_power_w == 0
    assert signals.battery_soc_pct == 0
    assert signals.house_load_total_w == 0
    assert signals.wallbox_power_w == 0
    assert signals.agate_inverter_on is False

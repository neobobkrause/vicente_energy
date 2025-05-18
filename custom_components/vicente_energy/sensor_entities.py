from homeassistant.components.sensor import SensorEntity

from .const import DOMAIN


class Budget24hSensor(SensorEntity):
    def __init__(self, coordinator):
        self.coordinator = coordinator

    @property
    def name(self):
        return "Vicente 24h Budget"

    @property
    def unique_id(self):
        return f"{self.coordinator.name}_budget_24h_kwh"

    @property
    def state(self):
        return self.coordinator.data.get("budget_24h_kwh")

class PowerLevelSensor(SensorEntity):
    def __init__(self, coordinator):
        self.coordinator = coordinator

    @property
    def name(self):
        return "Vicente Power Level"

    @property
    def unique_id(self):
        return f"{self.coordinator.name}_power_level_kw"

    @property
    def state(self):
        return self.coordinator.data.get("power_level_kw")

async def async_setup_entry(hass, entry, async_add_entities):
    hourly_coordinator = hass.data[DOMAIN][entry.entry_id]["hourly_coordinator"]
    minute_coordinator = hass.data[DOMAIN][entry.entry_id]["minute_coordinator"]

    sensors = [
        Budget24hSensor(hourly_coordinator),
        PowerLevelSensor(minute_coordinator),
    ]

    async_add_entities(sensors, True)

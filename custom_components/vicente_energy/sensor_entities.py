"""Lightweight sensor entities for coordinator values."""

from homeassistant.components.sensor import SensorEntity

from .const import DOMAIN


class Budget24hSensor(SensorEntity):
    """Expose the 24‑hour energy budget from the coordinator."""

    def __init__(self, coordinator):
        """Initialize with the hourly coordinator."""
        self.coordinator = coordinator

    @property
    def name(self):
        """Return the name of the sensor."""
        return "Vicente 24h Budget"

    @property
    def unique_id(self):
        """Return a unique identifier for this sensor."""
        return f"{self.coordinator.name}_budget_24h_kwh"

    @property
    def state(self):
        """Return the budget value from the coordinator."""
        return self.coordinator.data.get("budget_24h_kwh")

class PowerLevelSensor(SensorEntity):
    """Expose the instantaneous power level from the coordinator."""

    def __init__(self, coordinator):
        """Initialize with the minute coordinator."""
        self.coordinator = coordinator

    @property
    def name(self):
        """Return the name of the sensor."""
        return "Vicente Power Level"

    @property
    def unique_id(self):
        """Return a unique identifier for this sensor."""
        return f"{self.coordinator.name}_power_level_kw"

    @property
    def state(self):
        """Return the power level value from the coordinator."""
        return self.coordinator.data.get("power_level_kw")

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up Vicente Energy sensors via config entry."""
    hourly_coordinator = hass.data[DOMAIN][entry.entry_id]["hourly_coordinator"]
    minute_coordinator = hass.data[DOMAIN][entry.entry_id]["minute_coordinator"]

    sensors = [
        Budget24hSensor(hourly_coordinator),
        PowerLevelSensor(minute_coordinator),
    ]

    async_add_entities(sensors, True)

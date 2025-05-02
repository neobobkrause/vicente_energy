"""Sensors for Vicente Energy integration"""
import logging
from datetime import datetime, timezone
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    data = hass.data[DOMAIN]
    state_manager = data["state_manager"]
    hourly = data["hourly_coordinator"]
    minute = data["minute_coordinator"]

    sensors = [
        EstimatedHouseholdUseSensor(hourly, state_manager),
        SessionStartTimeSensor(minute),
        SessionDurationSensor(minute),
        SessionPowerUsedSensor(minute),
        BudgetRemainingSensor(hourly, minute),
    ]
    async_add_entities(sensors, True)

class EstimatedHouseholdUseSensor(CoordinatorEntity, SensorEntity):
    """24h household load estimate sensor"""
    _attr_name = "Estimated Household Use (kWh)"
    _attr_unique_id = f"{DOMAIN}_estimated_household_use"

    def __init__(self, coordinator, state_manager):
        super().__init__(coordinator)
        self.state_manager = state_manager

    @property
    def native_value(self):
        forecasts = getattr(self.state_manager, "load_forecasts", [])
        return sum(forecasts)

class SessionStartTimeSensor(CoordinatorEntity, SensorEntity):
    _attr_name = "Charging Session Start"
    _attr_unique_id = f"{DOMAIN}_session_start_time"

    def __init__(self, coordinator):
        super().__init__(coordinator)

    @property
    def native_value(self):
        return self.coordinator.hass.data[DOMAIN].get("session_start_time")

class SessionDurationSensor(CoordinatorEntity, SensorEntity):
    _attr_name = "Charging Session Duration (h)"
    _attr_unique_id = f"{DOMAIN}_session_duration_h"

    def __init__(self, coordinator):
        super().__init__(coordinator)

    @property
    def native_value(self):
        return self.coordinator.hass.data[DOMAIN].get("session_duration")

class SessionPowerUsedSensor(CoordinatorEntity, SensorEntity):
    _attr_name = "Charging Session Power Used (kWh)"
    _attr_unique_id = f"{DOMAIN}_session_power_used"

    def __init__(self, coordinator):
        super().__init__(coordinator)

    @property
    def native_value(self):
        return self.coordinator.hass.data[DOMAIN].get("session_kwh")

class BudgetRemainingSensor(CoordinatorEntity, SensorEntity):
    _attr_name = "Charging Budget Remaining (kWh)"
    _attr_unique_id = f"{DOMAIN}_budget_remaining"

    def __init__(self, hourly_coordinator, minute_coordinator):
        super().__init__(minute_coordinator)
        self.hourly = hourly_coordinator

    @property
    def native_value(self):
        budget = self.hourly.data.get("24h_budget", 0)
        used = self.coordinator.hass.data[DOMAIN].get("session_kwh", 0)
        return max(budget - used, 0)
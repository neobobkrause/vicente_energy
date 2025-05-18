
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import ENERGY_KILO_WATT_HOUR, POWER_KILO_WATT
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity

DOMAIN = "vicente_energy"

async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    sensors = [
        Budget24hSensor(data["hourly_coordinator"]),
        PowerLevelSensor(data["minute_coordinator"]),
        SessionStartTimeSensor(data["session"]),
        SessionDurationSensor(data["session"]),
        SessionEnergyUsedSensor(data["session"]),
        AvailableAfterSensor(data["session"]),
        ChargeStateSensor(data["session"])
    ]
    # Add location name sensor if provided
    loc_name = entry.options.get(CONF_LOCATION_NAME, entry.data.get(CONF_LOCATION_NAME))
    if loc_name:
        location_sensor = LocationNameSensor(entry.entry_id, loc_name)
        sensors.append(location_sensor)
        # store reference for dynamic updates
        hass.data[DOMAIN][entry.entry_id][CONF_LOCATION_NAME_ENTITY] = location_sensor
    async_add_entities(sensors, True)

class LocationNameSensor(SensorEntity):
    """Sensor to expose the configured location name."""

    def __init__(self, entry_id, location_name):
        self._attr_name = "Vicente Energy Location Name"
        self._entry_id = entry_id
        self._location_name = location_name or ""
        # Unique ID uses entry_id to ensure uniqueness per config entry
        self._attr_unique_id = f"{entry_id}_location_name"
        # no unit; categorize as diagnostic
        self._attr_entity_category = EntityCategory.DIAGNOSTIC


    @property
    def state(self):
        return self._location_name


    def set_location_name(self, name: str):
        """Update the stored location name (called on config changes)."""
        self._location_name = name or ""

class Budget24hSensor(CoordinatorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Vicente Energy 24h Budget"
        self._attr_unit_of_measurement = ENERGY_KILO_WATT_HOUR

    @property
    def state(self):
        return round(self.coordinator.data.get("budget_24h_kwh", 0.0), 3)

    @property
    def unique_id(self):
        # Use the coordinator's name (which is typically the entry_id or alias) to form a stable unique_id
        return f"{getattr(self.coordinator, 'name', 'vicente_energy')}_budget_24h_kwh"

class PowerLevelSensor(CoordinatorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Vicente Energy Power Level"
        self._attr_unit_of_measurement = POWER_KILO_WATT

    @property
    def state(self):
        return round(self.coordinator.data.get("power_level_kw", 0.0), 3)

    @property
    def unique_id(self):
        return f"{getattr(self.coordinator, 'name', 'vicente_energy')}_power_level_kw"

class SessionStartTimeSensor(CoordinatorEntity):
    def __init__(self, session):
        self._session = session
        self._attr_name = "Vicente Energy Session Start Time"

    @property
    def state(self):
        ts = self._session.session_start_time
        return ts.isoformat() if ts else None

class SessionDurationSensor(CoordinatorEntity):
    def __init__(self, session):
        self._session = session
        self._attr_name = "Vicente Energy Session Duration"

    @property
    def state(self):
        return int(self._session.session_duration.total_seconds() / 60) if self._session.session_duration else 0

class SessionEnergyUsedSensor(CoordinatorEntity):
    def __init__(self, session):
        self._session = session
        self._attr_name = "Vicente Energy Session kWh Used"
        self._attr_unit_of_measurement = ENERGY_KILO_WATT_HOUR

    @property
    def state(self):
        return round(self._session.session_kwh_used, 3)

class AvailableAfterSensor(CoordinatorEntity):
    def __init__(self, session):
        self._session = session
        self._attr_name = "Vicente Energy kWh Available After"
        self._attr_unit_of_measurement = ENERGY_KILO_WATT_HOUR

    @property
    def state(self):
        return round(self._session.session_available_after, 3)

class ChargeStateSensor(CoordinatorEntity):
    def __init__(self, session):
        self._session = session
        self._attr_name = "Vicente Energy Charge State"

    @property
    def state(self):
        return self._session.charge_state

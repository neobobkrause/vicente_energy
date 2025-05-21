
"""Home Assistant entrypoint for the Vicente Energy integration."""

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .services import ServiceType
from .const import (
    CONF_LOCATION_NAME,
    CONF_SESSION_LEARNING_ALPHA,
    CONF_SOLAR_FORECAST_ENTITIES,
    CONF_SOLAR_POWER_ENTITY,
    CONF_BATTERY_SOC_ENTITY,
    CONF_HOUSE_LOAD_ENTITY,
    CONF_EVCHARGER_POWER_ENTITY,
    CONF_EVCHARGER_STATE_ENTITY,
    DOMAIN
)
from .state_manager import StateManager
from .services.service_manager import ServiceManager
from .solar_adapter import SolarForecastAdapter
from .charge_estimator import ChargeEstimator
from .input_collector import InputCollector
from .session_manager import SessionManager

_LOGGER = logging.getLogger(__name__)


async def dummy_service(call):
    """Placeholder service handler."""
    _LOGGER.info("Service called: %s", call.data)

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up via YAML configuration (import into config flow)."""
    try:
        hass.async_create_task(
            hass.config_entries.flow.async_init(DOMAIN, context={"source": "import"}, data=config.get(DOMAIN, {}))
        )
    except AttributeError:
        await hass.config_entries.flow.async_init(DOMAIN, context={"source": "import"}, data=config.get(DOMAIN, {}))
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Vicente Energy from a config entry."""
    ev_charger = entry.options.get(ServiceType.EV_CHARGER_SERVICE, entry.data.get(ServiceType.EV_CHARGER_SERVICE, "none"))
    battery = entry.options.get(ServiceType.BATTERY_SERVICE, entry.data.get(ServiceType.BATTERY_SERVICE, "none"))
    solar_production = entry.options.get(ServiceType.SOLAR_SERVICE, entry.data.get(ServiceType.SOLAR_SERVICE, "none"))
    solar_forecast = entry.options.get(ServiceType.FORECAST_SERVICE, entry.data.get(ServiceType.FORECAST_SERVICE, "none"))
    location_name = entry.options.get(CONF_LOCATION_NAME, entry.data.get(CONF_LOCATION_NAME, ""))

    state = StateManager(hass, entry.entry_id)
    await state.async_load()
    state.data[CONF_SESSION_LEARNING_ALPHA] = entry.options.get(CONF_SESSION_LEARNING_ALPHA, entry.data.get(CONF_SESSION_LEARNING_ALPHA, 0.1))

    service_manager = ServiceManager(hass, solar_forecast, ev_charger)
    hass.loop.create_task(service_manager.connect_services())

    merged_conf = dict(entry.data)
    _LOGGER.debug("Merged config: %s", merged_conf)
    merged_conf.update(entry.options)

    solar_adapter = SolarForecastAdapter(hass, merged_conf.get(CONF_SOLAR_FORECAST_ENTITIES, []), state, service_manager)
    estimator = ChargeEstimator(merged_conf, state)

    collector = InputCollector(
        hass,
        merged_conf.get(CONF_SOLAR_POWER_ENTITY, ""),
        merged_conf.get(CONF_SOLAR_FORECAST_ENTITIES, []),
        merged_conf.get(CONF_BATTERY_SOC_ENTITY, ""),
        merged_conf.get(CONF_HOUSE_LOAD_ENTITY, ""),
        merged_conf.get(CONF_EVCHARGER_POWER_ENTITY, ""),
        wallbox_state_entity=merged_conf.get(CONF_EVCHARGER_STATE_ENTITY, ""),
        service_manager=service_manager
    )
    hass.services.async_register(DOMAIN, "set_power_level", dummy_service)
    hass.services.async_register(DOMAIN, "reset_history", dummy_service)

    async def hourly_update_method():
        raw = await solar_adapter.get_corrected_forecast()
        signals = collector.get_signals()
        return estimator.estimate(raw, signals)

    async def minute_update_method():
        signals = await collector.get_signals()
        return estimator.get_power_level(signals)

    hourly_coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"{DOMAIN}_hourly",
        update_interval=timedelta(hours=1),
        update_method=hourly_update_method,
    )

    minute_coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"{DOMAIN}_minute",
        update_interval=timedelta(minutes=1),
        update_method=minute_update_method,
    )

    internal_sensors = {
        CONF_SOLAR_POWER_ENTITY: "sensor.calculated_solar_power",
        CONF_BATTERY_SOC_ENTITY: "sensor.calculated_battery_soc",
        CONF_HOUSE_LOAD_ENTITY: "sensor.calculated_house_load",
        CONF_EVCHARGER_POWER_ENTITY: "sensor.calculated_charger_power",
        CONF_EVCHARGER_STATE_ENTITY: "sensor.calculated_wallbox_state",
    }
    coordinator = VicenteEnergyCoordinator(
        hass,
        internal_sensors,
        location_name,
        solar_forecast,
        ev_charger
    )
    await coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN][entry.entry_id] = coordinator
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    session = SessionManager(hass, state)

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "state_manager": state,
        "service_manager": service_manager,
        "hourly_coordinator": hourly_coordinator,
        "minute_coordinator": minute_coordinator,
        "collector": collector,
        "solar_adapter": solar_adapter,
        "estimator": estimator,
        "session": session,
    }

    entry.async_on_unload(entry.add_update_listener(async_update_options))

    await hourly_coordinator.async_config_entry_first_refresh()
    await minute_coordinator.async_config_entry_first_refresh()
    await hass.config_entries.async_forward_entry_setup(entry, "sensor")
    await async_register_services(hass, DOMAIN, session, state)
    return True


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry):
    """Handle option updates for Vicente Energy entry."""
    _LOGGER.info("Reconfiguring Vicente Energy due to updated options...")
    data = hass.data[DOMAIN].get(entry.entry_id)
    if not data:
        return

    sm: ServiceManager = data["service_manager"]
    sm.update_services(
        entry.options.get(ServiceType.FORECAST_SERVICE, entry.data.get(ServiceType.FORECAST_SERVICE, "none")),
        entry.options.get(ServiceType.EV_CHARGER_SERVICE, entry.data.get(ServiceType.EV_CHARGER_SERVICE, "none"))
    )

    collector: InputCollector = data.get("collector")
    if collector:
        collector.update_entities_from_entry(entry)

    location_entity = data.get("location_name_entity")
    if location_entity:
        new_name = entry.options.get(CONF_LOCATION_NAME, entry.data.get(CONF_LOCATION_NAME, ""))
        location_entity.set_location_name(new_name)
        location_entity.async_write_ha_state()

    await data["hourly_coordinator"].async_request_refresh()
    await data["minute_coordinator"].async_request_refresh()


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a Vicente Energy config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    if unload_ok and DOMAIN in hass.data and entry.entry_id in hass.data[DOMAIN]:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

class VicenteEnergyCoordinator(DataUpdateCoordinator):
    """Coordinator to publish calculated Vicente Energy values."""

    def __init__(self, hass, sensors, location_name, solar_forecast, ev_charger):
        """Initialize the coordinator with entity IDs and configuration."""
        self.hass = hass
        self.sensors = sensors
        self.location_name = location_name
        self.solar_forecast = solar_forecast
        self.ev_charger = ev_charger

        super().__init__(
            hass,
            _LOGGER,
            name="vicente_energy_hourly",
            update_interval=timedelta(hours=1),
        )

    async def _async_update_data(self):
        """Refresh calculated sensor values."""
        calculated_values = {
            "solar_power": 0,
            "battery_soc": 0,
            "house_load": 0,
            "wallbox_power": 0,
            "wallbox_state": "unplugged",
            "inverter_on": False
        }

        for key, value in calculated_values.items():
            entity_id = self.sensors[f"{key}_entity"]
            self.hass.states.async_set(entity_id, value)

        return calculated_values

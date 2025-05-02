import logging
from datetime import timedelta

import voluptuous as vol
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .input_collector import InputCollector
from .const import SIGNAL_HISTORY_LENGTH

DOMAIN = "vicente_energy"

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required("solar_power_entity"): str,
                vol.Required("solar_forecast_entities"): [str],
                vol.Required("battery_soc_entity"): str,
                vol.Required("house_load_entity"): str,
                vol.Required("wallbox_power_entity"): str,
                vol.Required("inverter_on_entity"): str,
                vol.Required("wallbox_state_entity"): str,
                vol.Optional("battery_capacity_kwh", default=0.0): float,
                vol.Optional("reserve_soc_pct", default=0.0): float,
                vol.Optional("storage_efficiency", default=1.0): float,
                vol.Optional("max_charger_power_kw", default=0.0): float,
                vol.Optional("session_learning_alpha", default=0.1): float,
                vol.Optional("budget_update_interval_hours", default=24): int,
                vol.Optional("update_interval_minutes", default=1): int,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

async def async_setup(hass: HomeAssistant, config: dict):
    conf = config.get(DOMAIN)
    if not conf:
        return True

    # Initialize input collector with explicit parameters
    collector = InputCollector(
        hass,
        conf["solar_power_entity"],
        conf["solar_forecast_entities"],
        conf["battery_soc_entity"],
        conf["house_load_entity"],
        conf["wallbox_power_entity"],
        conf["inverter_on_entity"],
        conf["wallbox_state_entity"],
        conf.get("battery_capacity_kwh", 0.0),
        conf.get("reserve_soc_pct", 0.0),
        conf.get("storage_efficiency", 1.0),
        conf.get("max_charger_power_kw", 0.0),
        conf.get("session_learning_alpha", 0.1),
        conf.get("budget_update_interval_hours", 24),
        conf.get("update_interval_minutes", 1),
    )

    # Create coordinators
    hourly_coordinator = DataUpdateCoordinator(
        hass,
        logging.getLogger(__name__),
        name="vicente_energy_hourly",
        update_method=collector.get_signals,
        update_interval=timedelta(hours=1),
    )
    minute_coordinator = DataUpdateCoordinator(
        hass,
        logging.getLogger(__name__),
        name="vicente_energy_minute",
        update_method=collector.get_signals,
        update_interval=timedelta(minutes=1),
    )

    await hourly_coordinator.async_config_entry_first_refresh()
    await minute_coordinator.async_config_entry_first_refresh()

    # Store coordinators and state_manager
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN]["hourly_coordinator"] = hourly_coordinator
    hass.data[DOMAIN]["minute_coordinator"] = minute_coordinator
    hass.data[DOMAIN]["state_manager"] = collector.state_manager

    # Service handlers
    async def set_power_level_service(call):
        level = call.data.get("power_level_kw")
        collector.state_manager.set_power_level(level)

    async def reset_history_service(call):
        sm = collector.state_manager
        sm.reset_history()

    # Register services
    hass.services.async_register(DOMAIN, "set_power_level", set_power_level_service)
    hass.services.async_register(DOMAIN, "reset_history", reset_history_service)

    return True

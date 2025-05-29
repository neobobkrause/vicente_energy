
"""Home Assistant entrypoint for the Vicente Energy integration."""

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .services import ServiceType
from .services.budget_service import ChargingBudgetService
from .services.charging_session_service import ChargingSessionService
from .entity_manager import EntityManager
from .const import (
    CONF_LOCATION_NAME,
    DOMAIN
)
from .services.service_manager import ServiceManager

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up via YAML configuration (import into config flow)."""
    try:
        hass.async_create_task(
            hass.config_entries.flow.async_init(DOMAIN,
                                                context={"source": "import"},
                                                data=config.get(DOMAIN, {}))
        )
    except AttributeError:
        await hass.config_entries.flow.async_init(DOMAIN,
                                                  context={"source": "import"},
                                                  data=config.get(DOMAIN, {}))
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Vicente Energy from a config entry."""

    # Initialize  services
    service_ids: dict[ServiceType, str] = {}
    service_ids[ServiceType.EV_CHARGER_SERVICE] =\
        entry.options.get(ServiceType.EV_CHARGER_SERVICE,
                          entry.data.get(ServiceType.EV_CHARGER_SERVICE, "default"))
    service_ids[ServiceType.BATTERY_SERVICE] =\
        entry.options.get(ServiceType.BATTERY_SERVICE,
                          entry.data.get(ServiceType.BATTERY_SERVICE, "default"))
    service_ids[ServiceType.SOLAR_SERVICE] =\
        entry.options.get(ServiceType.SOLAR_SERVICE,
                          entry.data.get(ServiceType.SOLAR_SERVICE, "default"))
    service_ids[ServiceType.FORECAST_SERVICE] =\
        entry.options.get(ServiceType.FORECAST_SERVICE,
                          entry.data.get(ServiceType.FORECAST_SERVICE, "default"))
    service_ids[ServiceType.GRID_SERVICE] =\
        entry.options.get(ServiceType.GRID_SERVICE,
                          entry.data.get(ServiceType.GRID_SERVICE, "default"))
    service_ids[ServiceType.BUDGET_SERVICE] =\
        entry.options.get(ServiceType.BUDGET_SERVICE,
                          entry.data.get(ServiceType.BUDGET_SERVICE, "default"))
    service_ids[ServiceType.CHARGING_SERVICE] =\
        entry.options.get(ServiceType.CHARGING_SERVICE,
                          entry.data.get(ServiceType.CHARGING_SERVICE, "default"))
    location_name = entry.options.get(CONF_LOCATION_NAME,
                                      entry.data.get(CONF_LOCATION_NAME, ""))

    # Initialize EntityManager
    entity_manager: EntityManager = EntityManager(hass, entry)

    # Register Location Name entity.
    await entity_manager.register_entity(
        entity_id = "ve_location_name",
        entity_type = "sensor",
        unit = "",
        description = "Vicente Energy Location"
    )
    await entity_manager.update_entity(
        "ve_location_name",
        location_name,
        {
            "icon": "mdi:home",
            "friendly_name": "Vicente Energy Location Name"
        }
    )

    # Initialize service manager
    service_manager = ServiceManager(hass, service_ids)
    await service_manager.update_services(service_ids, False)

    hass.loop.create_task(service_manager.connect_services())

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
         "entity_manager": entity_manager,
         "service_manager": service_manager,
     }

    # Initialize services explicitly
    await service_manager.connect_services()

    # Set up platforms (e.g., sensor entities managed by EntityManager)
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    return True

async def async_update_options(hass: HomeAssistant, entry: ConfigEntry):
    """Handle option updates for Vicente Energy entry."""
    _LOGGER.info("Reconfiguring Vicente Energy due to updated options...")
    data = hass.data[DOMAIN].get(entry.entry_id)
    if not data:
        return

    service_ids: dict[ServiceType, str] = {}
    service_ids[ServiceType.EV_CHARGER_SERVICE] =\
        entry.options.get(ServiceType.EV_CHARGER_SERVICE,
                          entry.data.get(ServiceType.EV_CHARGER_SERVICE, "default"))
    service_ids[ServiceType.BATTERY_SERVICE] =\
        entry.options.get(ServiceType.BATTERY_SERVICE,
                          entry.data.get(ServiceType.BATTERY_SERVICE, "default"))
    service_ids[ServiceType.SOLAR_SERVICE] =\
        entry.options.get(ServiceType.SOLAR_SERVICE,
                          entry.data.get(ServiceType.SOLAR_SERVICE, "default"))
    service_ids[ServiceType.FORECAST_SERVICE] =\
        entry.options.get(ServiceType.FORECAST_SERVICE,
                          entry.data.get(ServiceType.FORECAST_SERVICE, "default"))
    service_ids[ServiceType.GRID_SERVICE] =\
        entry.options.get(ServiceType.GRID_SERVICE,
                          entry.data.get(ServiceType.GRID_SERVICE, "default"))
    service_ids[ServiceType.BUDGET_SERVICE] =\
        entry.options.get(ServiceType.BUDGET_SERVICE,
                          entry.data.get(ServiceType.BUDGET_SERVICE, "default"))
    service_ids[ServiceType.CHARGING_SERVICE] =\
        entry.options.get(ServiceType.CHARGING_SERVICE,
                          entry.data.get(ServiceType.CHARGING_SERVICE, "default"))
    location_name = entry.options.get(CONF_LOCATION_NAME,
                                      entry.data.get(CONF_LOCATION_NAME, ""))

    service_manager: ServiceManager = data["service_manager"]
    await service_manager.update_services(service_ids, True)

    entity_manager: EntityManager = data["entity_manager"]
    await entity_manager.update_entity("ve_location_name", location_name)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a Vicente Energy config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    if unload_ok and DOMAIN in hass.data and entry.entry_id in hass.data[DOMAIN]:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

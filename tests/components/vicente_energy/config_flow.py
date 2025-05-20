"""Config flow for Vicente Energy Integration"""
import voluptuous as vol

from homeassistant import config_entries

from . import DOMAIN

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_SOLAR_POWER_ENTITY): str,
        vol.Required(CONF_SOLAR_FORECAST_ENTITIES): list,
        vol.Required(CONF_BATTERY_SOC_ENTITY): str,
        vol.Required(CONF_HOUSE_LOAD_ENTITY): str,
        vol.Required(CONF_WALLBOX_POWER_ENTITY): str,
        vol.Required(CONF_INVERTER_ON_ENTITY): str,
        vol.Required(CONF_WALLBOX_STATE_ENTITY): str,
    }
)


class VicenteEnergyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA)
        # create entry
        return self.async_create_entry(title="Vicente Energy", data=user_input)

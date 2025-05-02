"""Config flow for Vicente Energy Integration"""
import voluptuous as vol
from homeassistant import config_entries
from . import DOMAIN

DATA_SCHEMA = vol.Schema({
    vol.Required("solar_power_entity"): str,
    vol.Required("solar_forecast_entities"): list,
    vol.Required("battery_soc_entity"): str,
    vol.Required("house_load_entity"): str,
    vol.Required("wallbox_power_entity"): str,
    vol.Required("inverter_on_entity"): str,
    vol.Required("wallbox_state_entity"): str,
})

class VicenteFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA)
        # create entry
        return self.async_create_entry(title="Vicente Energy", data=user_input)
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
    vol.Required("battery_capacity_kwh", default=10.0): float,
    vol.Required("reserve_soc_pct", default=20.0): float,
    vol.Required("storage_efficiency", default=0.9): float,
    vol.Required("max_charger_power_kw", default=7.4): float,
    vol.Required("session_learning_alpha", default=0.1): float,
    vol.Optional("budget_update_interval_hours", default=1): int,
    vol.Optional("update_interval_minutes", default=1): int,
})

class VicenteFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self):
        self._data = {}

    async def async_step_user(self, user_input=None):
        if user_input is None:
            return await self.async_show_form(
                step_id="user", data_schema=DATA_SCHEMA
            )
        self._data = user_input
        return await self.async_create_entry(
            title="Vicente Energy", data=self._data
        )

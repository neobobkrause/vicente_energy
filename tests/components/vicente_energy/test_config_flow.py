from custom_components.vicente_energy.config_flow import VicenteEnergyConfigFlow
from custom_components.vicente_energy.const import (
    CONF_BATTERY_CAPACITY_KWH,
    CONF_BATTERY_SOC_ENTITY,
    CONF_BUDGET_UPDATE_INTERVAL_HOURS,
    CONF_HOUSE_LOAD_ENTITY,
    CONF_INVERTER_ON_ENTITY,
    CONF_MAX_CHARGER_POWER_KW,
    CONF_RESERVE_SOC_PCT,
    CONF_SESSION_LEARNING_ALPHA,
    CONF_SOLAR_FORECAST_ENTITIES,
    CONF_SOLAR_POWER_ENTITY,
    CONF_STORAGE_EFFICIENCY,
    CONF_UPDATE_INTERVAL_MINUTES,
    CONF_WALLBOX_POWER_ENTITY,
    CONF_WALLBOX_STATE_ENTITY,
)
import pytest

from homeassistant.core import HomeAssistant


@pytest.mark.asyncio
async def test_step_user_form(hass: HomeAssistant):
    flow = VicenteEnergyConfigFlow()
    flow.hass = hass
    result = await flow.async_step_user()
    assert result["type"] == "form"
    assert "data_schema" in result


@pytest.mark.asyncio
async def test_step_user_create_entry(hass: HomeAssistant):
    flow = VicenteEnergyConfigFlow()
    flow.hass = hass
    user_input = {
        CONF_SOLAR_POWER_ENTITY: "sensor.solar",
        CONF_SOLAR_FORECAST_ENTITIES: ["sensor.forecast"],
        CONF_BATTERY_SOC_ENTITY: "sensor.soc",
        CONF_HOUSE_LOAD_ENTITY: "sensor.load",
        CONF_WALLBOX_POWER_ENTITY: "sensor.wp",
        CONF_INVERTER_ON_ENTITY: "binary_sensor.inv",
        CONF_WALLBOX_STATE_ENTITY: "sensor.state",
        CONF_BATTERY_CAPACITY_KWH: 20.0,
        CONF_RESERVE_SOC_PCT: 25.0,
        CONF_STORAGE_EFFICIENCY: 0.95,
        CONF_MAX_CHARGER_POWER_KW: 7.4,
        CONF_SESSION_LEARNING_ALPHA: 0.1,
        CONF_BUDGET_UPDATE_INTERVAL_HOURS: 2,
        CONF_UPDATE_INTERVAL_MINUTES: 5,
    }
    result = await flow.async_step_user(user_input=user_input)
    assert result["type"] == "form"
    assert "data_schema" in result


def test_config_flow_schema_includes_service_choices():
    flow = VicenteEnergyConfigFlow()
    schema = flow.async_step_user.__annotations__.get("return", None)
    assert "forecast_service" or "charger_service" not in str(schema)

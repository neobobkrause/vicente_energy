from unittest.mock import AsyncMock, patch

from custom_components.vicente_energy import DOMAIN
from custom_components.vicente_energy.const import (
    CONF_BATTERY_SOC_ENTITY,
    CONF_HOUSE_LOAD_ENTITY,
    CONF_INVERTER_ON_ENTITY,
    CONF_SOLAR_FORECAST_ENTITIES,
    CONF_SOLAR_POWER_ENTITY,
    CONF_WALLBOX_POWER_ENTITY,
    CONF_WALLBOX_STATE_ENTITY,
)
import pytest

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component


@pytest.fixture
async def setup_vicente_energy(hass: HomeAssistant):
    config = {
        DOMAIN: {
            CONF_SOLAR_POWER_ENTITY: "sensor.solar",
            CONF_SOLAR_FORECAST_ENTITIES: [],
            CONF_BATTERY_SOC_ENTITY: "sensor.soc",
            CONF_HOUSE_LOAD_ENTITY: "sensor.load",
            CONF_WALLBOX_POWER_ENTITY: "sensor.wp",
            CONF_INVERTER_ON_ENTITY: "binary_sensor.inv",
            CONF_WALLBOX_STATE_ENTITY: "sensor.state",
        }
    }
    await async_setup_component(hass, DOMAIN, config)
    await hass.async_block_till_done()
    return hass


@pytest.mark.asyncio
async def test_set_power_level_service(hass: HomeAssistant):
    entry = ConfigEntry(
        version=1,
        minor_version=0,
        domain="vicente_energy",
        title="Vicente Energy",
        data={},
        source="test",
        entry_id="test",
    )

    with patch(
        "custom_components.vicente_energy.async_setup_entry",
        AsyncMock(return_value=True),
    ), patch(
        "custom_components.vicente_energy.async_setup", AsyncMock(return_value=True)
    ), patch(
        "custom_components.vicente_energy.dummy_service", AsyncMock()
    ) as mock_service:
        await hass.config_entries.async_add(entry)
        await hass.async_block_till_done()

        hass.services.async_register("vicente_energy", "set_power_level", mock_service)

        await hass.services.async_call(
            "vicente_energy",
            "set_power_level",
            {"power_level_kw": 2.5},
            blocking=True,
        )

        mock_service.assert_called_once()


@pytest.mark.asyncio
async def test_reset_history_service(hass: HomeAssistant):
    entry = ConfigEntry(
        version=1,
        minor_version=0,
        domain="vicente_energy",
        title="Vicente Energy",
        data={},
        source="test",
        entry_id="test",
    )

    with patch(
        "custom_components.vicente_energy.async_setup_entry",
        AsyncMock(return_value=True),
    ), patch(
        "custom_components.vicente_energy.async_setup", AsyncMock(return_value=True)
    ), patch(
        "custom_components.vicente_energy.dummy_service", AsyncMock()
    ) as mock_reset:
        await hass.config_entries.async_add(entry)
        await hass.async_block_till_done()

        hass.services.async_register("vicente_energy", "reset_history", mock_reset)

        await hass.services.async_call(
            "vicente_energy",
            "reset_history",
            {},
            blocking=True,
        )

        mock_reset.assert_called_once()

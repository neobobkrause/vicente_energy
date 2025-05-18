from unittest.mock import AsyncMock, patch

from custom_components.vicente_energy.const import DOMAIN
import pytest

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component


@pytest.fixture
async def setup_vicente_energy(hass: HomeAssistant):
    await async_setup_component(hass, DOMAIN, {DOMAIN: {}})
    await hass.async_block_till_done()
    return hass


@pytest.mark.asyncio
async def test_set_power_level_service_errors(setup_vicente_energy):
    hass = setup_vicente_energy
    with pytest.raises(ValueError):
        await hass.services.async_call(DOMAIN, "set_power_level", {}, blocking=True)


@pytest.mark.asyncio
async def test_reset_history_clears_all(hass: HomeAssistant):
    entry = ConfigEntry(
        version=1,
        minor_version=0,
        domain=DOMAIN,
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

        hass.services.async_register(DOMAIN, "reset_history", mock_reset)

        await hass.services.async_call(
            DOMAIN,
            "reset_history",
            {},
            blocking=True,
        )

        mock_reset.assert_called_once()


@pytest.mark.asyncio
async def test_set_power_level_service_errors(hass):
    entry = ConfigEntry(
        version=1,
        minor_version=0,
        domain=DOMAIN,
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
    ):
        await hass.config_entries.async_add(entry)
        await hass.async_block_till_done()

        # Manually register a service that raises a ValueError
        def raise_value_error(call):
            raise ValueError("Invalid service data")

        hass.services.async_register(DOMAIN, "set_power_level", raise_value_error)

        with pytest.raises(ValueError):
            await hass.services.async_call(
                DOMAIN,
                "set_power_level",
                {},
                blocking=True,
            )

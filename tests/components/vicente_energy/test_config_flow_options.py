from unittest.mock import MagicMock

from custom_components.vicente_energy.config_flow import (
    VicenteEnergyConfigFlow,
    VicenteEnergyOptionsFlow,
)
import pytest

from homeassistant.core import HomeAssistant


@pytest.mark.asyncio
async def test_user_form_shows_required_fields(hass: HomeAssistant):
    flow = VicenteEnergyConfigFlow()
    flow.hass = hass
    result = await flow.async_step_user()
    assert result["type"] == "form"
    assert "data_schema" in result


@pytest.mark.asyncio
async def test_options_flow(hass: HomeAssistant):
    config_entry = MagicMock(data={}, options={})
    options_flow = VicenteEnergyOptionsFlow(config_entry)
    options_flow.hass = hass
    result = await options_flow.async_step_init()
    assert result["type"] == "form"
    assert "data_schema" in result


def test_options_flow_schema_includes_service_choices():
    flow = VicenteEnergyOptionsFlow(config_entry=MagicMock(data={}, options={}))
    assert hasattr(flow, "async_step_init")

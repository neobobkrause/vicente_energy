from unittest.mock import AsyncMock, patch

from custom_components.vicente_energy.sensor import LocationNameSensor
from custom_components.vicente_energy.services.service_manager import ServiceManager
from custom_components.vicente_energy.services.solcast_service import SolcastService
from custom_components.vicente_energy.services.wallbox_service import WallboxService
import pytest

from homeassistant.core import HomeAssistant


@pytest.mark.asyncio
async def test_service_manager_instantiates_correct_services(hass: HomeAssistant):
    sm = ServiceManager(hass, forecast_type="solcast", charger_type="wallbox")
    assert isinstance(sm.forecast_service, SolcastService)
    assert isinstance(sm.charger_service, WallboxService)

    sm_none = ServiceManager(hass, forecast_type="none", charger_type="none")
    assert sm_none.forecast_service is None
    assert sm_none.charger_service is None


@pytest.mark.asyncio
async def test_service_manager_handles_invalid_types_gracefully(
    hass: HomeAssistant, caplog
):
    sm = ServiceManager(
        hass, forecast_type="unknown_forecast", charger_type="invalid_charger"
    )
    assert sm.forecast_service is None
    assert sm.charger_service is None
    assert "Unknown forecast service type" in caplog.text
    assert "Unknown charger service type" in caplog.text


@patch(
    "custom_components.vicente_energy.services.wallbox_service.WallboxService.connect",
    new_callable=AsyncMock,
)
@pytest.mark.asyncio
async def test_service_manager_dynamic_switching(hass: HomeAssistant):
    sm = ServiceManager(hass, forecast_type="solcast", charger_type="wallbox")
    assert isinstance(sm.forecast_service, SolcastService)
    assert isinstance(sm.charger_service, WallboxService)

    sm.update_services(forecast_type="none", charger_type="none")
    assert sm.forecast_service is None
    assert sm.charger_service is None

    sm.update_services(forecast_type="none", charger_type="wallbox")
    assert sm.forecast_service is None
    assert isinstance(sm.charger_service, WallboxService)


@pytest.mark.asyncio
async def test_location_name_sensor_behavior():
    sensor = LocationNameSensor(entry_id="abc123", location_name="Vicente Road")
    assert sensor.name == "Vicente Energy Location Name"
    assert sensor.unique_id == "abc123_location_name"
    assert sensor.state == "Vicente Road"

    sensor.set_location_name("New Location")
    assert sensor.state == "New Location"

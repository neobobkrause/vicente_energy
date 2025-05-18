import logging

_LOGGER = logging.getLogger(__name__)
import asyncio

from .solcast_service import SolcastService
from .wallbox_service import WallboxEVChargerService


class ServiceManager:
    def __init__(self, hass, forecast_type: str = "none", charger_type: str = "none"):
        """Initialize the ServiceManager with specified service types."""
        self.hass = hass
        self.forecast_type = forecast_type
        self.charger_type = charger_type
        self.forecast_service = None
        self.charger_service = None
        # Instantiate forecast service if configured
        if forecast_type and forecast_type.lower() != "none":
            try:
                if forecast_type.lower() == "solcast":
                    self.forecast_service = SolcastService(hass)
                else:
                    raise ValueError(f"Unknown forecast service type: {forecast_type}")
            except Exception as e:
                _LOGGER.error("Failed to initialize forecast service '%s': %s", forecast_type, e)
                self.forecast_service = None
        # Instantiate EV charger service if configured
        if charger_type and charger_type.lower() != "none":
            try:
                if charger_type.lower() == "wallbox":
                    self.charger_service = WallboxEVChargerService(hass)
                else:
                    raise ValueError(f"Unknown charger service type: {charger_type}")
            except Exception as e:
                _LOGGER.error("Failed to initialize charger service '%s': %s", charger_type, e)
                self.charger_service = None


    async def connect_services(self):
        """Connect to external services asynchronously (if any)."""
        tasks = []
        if self.forecast_service:
            tasks.append(self.forecast_service.connect())
        if self.charger_service:
            tasks.append(self.charger_service.connect())
        if tasks:
            await asyncio.gather(*tasks)


    def update_services(self, forecast_type: str, charger_type: str):
        """Dynamically update the service types and reinitialize services."""
        _LOGGER = logging.getLogger(__name__)
        # Update forecast service if changed
        if forecast_type.lower() != (self.forecast_type.lower() if self.forecast_type else "none"):
            if self.forecast_service:
                _LOGGER.info("Shutting down forecast service: %s", self.forecast_type)
            self.forecast_type = forecast_type
            self.forecast_service = None
            if forecast_type.lower() != "none":
                try:
                    if forecast_type.lower() == "solcast":
                        self.forecast_service = SolcastService(self.hass)
                    else:
                        raise ValueError(f"Unknown forecast service type: {forecast_type}")
                except Exception as e:
                    _LOGGER.error("Failed to initialize forecast service '%s': %s", forecast_type, e)
                    self.forecast_service = None
            if self.forecast_service:
                # Start connection for new service
                self.hass.loop.create_task(self.forecast_service.connect())
        # Update charger service if changed
        if charger_type.lower() != (self.charger_type.lower() if self.charger_type else "none"):
            if self.charger_service:
                _LOGGER.info("Shutting down charger service: %s", self.charger_type)
            self.charger_type = charger_type
            self.charger_service = None
            if charger_type.lower() != "none":
                try:
                    if charger_type.lower() == "wallbox":
                        self.charger_service = WallboxEVChargerService(self.hass)
                    else:
                        raise ValueError(f"Unknown charger service type: {charger_type}")
                except Exception as e:
                    _LOGGER.error("Failed to initialize charger service '%s': %s", charger_type, e)
                    self.charger_service = None
            if self.charger_service:
                self.hass.loop.create_task(self.charger_service.connect())

    async def get_forecast(self):
        if not self.forecast_service:
            return {}  # No external service, forecast will come from sensors
        return await self.forecast_service.get_forecast()


    async def get_charger_state(self):
        if not self.charger_service:
            return {}  # No external service, charger state from sensors
        return await self.charger_service.get_charger_state()


    def register_forecast_callback(self, cb):
        if self.forecast_service:
            self.forecast_service.register_callback(cb)


    def register_charger_callback(self, cb):
        if self.charger_service:
            self.charger_service.register_callback(cb)

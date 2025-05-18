import asyncio
import logging

from .forecast_service import ForecastService

_LOGGER = logging.getLogger(__name__)

class SolcastService(ForecastService):
    def __init__(self, hass):
        self.hass = hass
        self._callbacks = []

    async def connect(self):
        while 'solcast' not in self.hass.data:
            _LOGGER.error("Solcast service unavailable, retrying in 60 seconds...")
            await asyncio.sleep(60)
        _LOGGER.info("Successfully connected to Solcast service.")

    async def get_forecast(self):
        return self.hass.data.get('solcast', {}).get('forecast', {})

    def register_callback(self, callback: Callable[[str, State], None]) -> None:
        self._callbacks.append(callback)

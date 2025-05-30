"""Adapter that provides solar forecast data to the estimator."""

import logging

_LOGGER = logging.getLogger(__name__)

class SolarForecastAdapter:
    """Fetch and correct solar forecast data from sensors or services."""

    def __init__(self, hass, forecast_entities, state_manager, service_manager=None):
        """Initialize with Home Assistant objects and configuration."""
        self.hass = hass
        self.state = state_manager
        self.service_manager = service_manager
        self._forecast_entities = list(forecast_entities) if forecast_entities is not None else []

    async def get_raw_forecast(self):
        """Return a list of forecast values from configured sources."""
        raw_forecast = []
        # If an external forecast service is configured, try that first
        if self.service_manager and getattr(self.service_manager, "forecast_service", None):
            forecast_data = await self.service_manager.get_forecast()
            if isinstance(forecast_data, dict) and "values" in forecast_data:
                try:
                    raw_list = forecast_data["values"]
                    raw_forecast = [float(x) for x in raw_list]
                except Exception:
                    raw_forecast = []
            elif isinstance(forecast_data, list):
                try:
                    raw_forecast = [float(x) for x in forecast_data]
                except Exception:
                    raw_forecast = []
            # Limit to 48 data points (24h) if more were returned
            if len(raw_forecast) > 48:
                raw_forecast = raw_forecast[:48]
        # If no external data was obtained, fall back to sensor-provided forecast(s)
        if not raw_forecast:
            for entity_id in self._forecast_entities:
                state = self.hass.states.get(entity_id)
                if state and hasattr(state, "state"):
                    try:
                        raw_forecast.append(float(state.state))
                    except ValueError:
                        raw_forecast.append(0.0)
        return raw_forecast

    async def get_corrected_forecast(self):
        """Return forecast adjusted by learned solar bias."""
        raw_forecast = await self.get_raw_forecast()
        bias = self.state.get_solar_bias()
        corrected = [max(f * (1 + bias), 0.0) for f in raw_forecast]
        _LOGGER.debug(f"Corrected solar forecast calculated: {corrected}")
        return corrected


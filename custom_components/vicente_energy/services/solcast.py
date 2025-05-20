import asyncio
import logging

from .forecast_service import ForecastService

_LOGGER = logging.getLogger(__name__)

class SolcastService(ForecastService):
    def __init__(self, hass: Optional[HomeAssistant]) -> None:
        self._today_hourly_production_kwh: Optional[List[float]] = None
        self._tomorrow_hourly_production_kwh: Optional[List[float]] = None

        # Define handlers
        handlers: dict[str, VEEntityStateChangeHandler] = {
            "sensor.solcast_pv_forecast_forecast_today": self._handle_today_production_change,
            "sensor.solcast_pv_forecast_forecast_tomorrow": self._handle_tomorrow_production_change,
            "sensor.solcast_pv_forecast_power_now": self._handle_now_production_change,
        }
        super().__init__(hass, handlers)

    async def connect(self):
        await super().connect()
        self.get_today_production_kwh()
        self.get_tomorrow_production_kwh()

    async def get_today_production_kwh(self) -> float:
        if len(self._today_hourly_production_kwh) != 24:
            self._get_today_hour_production_kwh(0)
            
        return _today_production_kwh

    async def get_tomorrow_production_kwh(self) -> float:
        if len(self._tomorrow_hourly_production_kwh) != 24:
            self._get_today_hour_production_kwh(0)
            
        return _tomorrow_production_kwh

    async def _get_today_hour_production_kwh(self, hour: int) -> float:
        if len(self._today_hourly_production_kwh) != 24:
            state = hass.states.get("sensor.solcast_pv_forecast_forecast_today")
            self._today_hourly_production_kwh = self._get_hourly_production_forecast(state)
        
            total: float = 0.0
            for i in self._today_hourly_production_kwh:
                total += self._today_hourly_production_kwh[i]     
            self._today_production_kwh = total  
        
        return self._today_hourly_production_kwh[hour]

    async def _get_tomorrow_hour_production_kwh(self, hour: int) -> float:
        if len(self._tomorrow_hourly_production_kwh) != 24:
            state = hass.states.get("sensor.solcast_pv_forecast_forecast_tomorrow")
            self._today_hourly_production_kwh = self._get_hourly_production_forecast(state)
        
            total: float = 0.0
            for i in self._tomorrow_hourly_production_kwh:
                total += self._tomorrow_hourly_production_kwh[i]     
            self._tomorrow_production_kwh = total  
        
        return self._tomorrow_hourly_production_kwh[hour]
        
    def _handle_today_production_change(self, entity_id, old_state, new_state) -> bool:
        try:
            values = self._get_hourly_production_forecast(new_state)
        except ValueError:
            _LOGGER.warning("Failed to parse Forecast.Solar production today from state: %s", new_state.state)
            return False
            
        self._today_production_kwh = values
        _LOGGER.debug("Forecast.Solar production today now updated")
        return True

    def _handle_tomorrow_production_change(self, entity_id, old_state, new_state) -> bool:
        try:
            values = self._get_hourly_production_forecast(new_state)
        except ValueError:
            _LOGGER.warning("Failed to parse Forecast.Solar production tomorrow from state: %s", new_state.state)
            return False

        self._tomorrow_hourly_production_kwh = values
        _LOGGER.debug("Forecast.Solar production tomorrow now updated")
        return True

    def _handle_now_production_change(self, entity_id, old_state, new_state) -> bool:
        try:
            value = float(new_state.state)
        except ValueError:
            _LOGGER.warning("Failed to parse Forecast.Solar production today from state: %s", new_state.state)
            return False
        
        if self._now_production_kw == value:
            return False
            
        self._now_production_kw = value
        _LOGGER.debug("Forecast.Solar production now updated: %.2f", value)
        return True

    async def _get_hourly_production_forecast(self, state) -> List[float]:
        if state is None or state.attributes.get("detailedForecast") is None:
            raise ValueError(f"Sensor {entity_id} or its 'detailedForecast' attribute is unavailable.")

        detailed_forecast = state.attributes["detailedForecast"]

        if len(detailed_forecast) < 48:
            raise ValueError(f"Expected at least 48 forecast entries, got {len(detailed_forecast)}.")

        hourly_forecast = []
        for i in range(0, 48, 2):
            estimate1 = detailed_forecast[i].get("pv_estimate", 0)
            estimate2 = detailed_forecast[i + 1].get("pv_estimate", 0)
            hourly_total = float(estimate1) + float(estimate2)
            hourly_forecast.append(hourly_total)

        return hourly_forecast
        

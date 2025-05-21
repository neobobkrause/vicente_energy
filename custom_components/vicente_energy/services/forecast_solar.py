"""Service wrapper for the Forecast.Solar integration."""

from datetime import datetime
import logging
from typing import List, cast

from homeassistant.core import HomeAssistant, State

from .service import VEEntityStateChangeHandler
from .forecast_service import ForecastService

_LOGGER = logging.getLogger(__name__)

class ForecastSolarService(ForecastService):
    """Handle Forecast.Solar sensor values."""

    def __init__(self, hass: HomeAssistant) -> None:
        self._today_hourly_production_kwh: List[float] = [0.0] * 24
        self._tomorrow_hourly_production_kwh: List[float] = [0.0] * 24

        # Define handlers
        handlers: dict[str, VEEntityStateChangeHandler] = {
            "sensor.energy_current_hour": self._handle_current_hour_change,
            "sensor.energy_next_hour": self._handle_next_hour_change,
            "sensor.power_production_now": self._handle_now_production_change,
            "sensor.energy_production_today": self._handle_today_production_change,
            "sensor.energy_production_tomorrow": self._handle_tomorrow_production_change,
        }
        super().__init__(hass, handlers)

    async def connect(self):
        await super().connect()

        # Prime the data members
        try:
            state: State = cast(State, self._hass.states.get("sensor.energy_production_today"))
            self._today_production_kwh = float(state.state)

            state = cast(State, self._hass.states.get("sensor.energy_production_tomorrow"))
            self._tomorrow_production_kwh = float(state.state)

            state = cast(State, self._hass.states.get("sensor.power_production_now"))
            self._now_production_kw = float(state.state)

            current_hour = datetime.now().hour  # 0 through 23
            state = cast(State, self._hass.states.get("sensor.energy_current_hour"))
            self._today_hourly_production_kwh[current_hour] = float(state.state)
            if current_hour is 23:
                self._tomorrow_hourly_production_kwh[0] = float(state.state)
            else:
                self._today_hourly_production_kwh[current_hour+1] = float(state.state)

        except ValueError:
            _LOGGER.warning("Failed to prime Forecast.Solar state: %s", state.state)

    async def _get_today_hour_production_kwh(self, hour: int) -> float:
        return self._today_hourly_production_kwh[hour]

    async def _get_tomorrow_hour_production_kwh(self, hour: int) -> float:
        return self._tomorrow_hourly_production_kwh[hour]

    def _handle_current_hour_change(self, entity_id, old_state, new_state) -> bool:
        try:
            current_hour = datetime.now().hour  # 0 through 23
            value = float(new_state.state)
        except ValueError:
            _LOGGER.warning("Failed to parse Forecast.Solar current hour forecast from state: %s",
                            new_state.state)
            return False

        if self._today_hourly_production_kwh[current_hour] == value:
            return False

        self._today_hourly_production_kwh[current_hour] = value
        _LOGGER.debug("Forecast.Solar current hour forecast updated: %.2f", value)

        return True

    def _handle_next_hour_change(self, entity_id, old_state, new_state) -> bool:
        try:
            current_hour = datetime.now().hour  # 0 through 23
            value = float(new_state.state)
        except ValueError:
            _LOGGER.warning("Failed to parse Forecast.Solar next hour forecast from state: %s",
                            new_state.state)
            return False

        if current_hour == 23:
            if self._tomorrow_hourly_production_kwh[0] == value:
                return False
            self._tomorrow_hourly_production_kwh[0] = value
        else:
            if self._today_hourly_production_kwh[current_hour+1] == value:
                return False
            self._today_hourly_production_kwh[current_hour+1] = value

        _LOGGER.debug("Forecast.Solar next hour forecast updated: %.2f", value)
        return True

    def _handle_now_production_change(self, entity_id, old_state, new_state) -> bool:
        try:
            value = float(new_state.state)
        except ValueError:
            _LOGGER.warning("Failed to parse Forecast.Solar production now from state: %s",
                            new_state.state)
            return False

        if self._now_production_kw == value:
            return False

        self._now_production_kw = value
        _LOGGER.debug("Forecast.Solar production now updated: %.2f", value)
        return True

    def _handle_today_production_change(self, entity_id, old_state, new_state) -> bool:
        try:
            value = float(new_state.state)
        except ValueError:
            _LOGGER.warning("Failed to parse Forecast.Solar production today from state: %s",
                            new_state.state)
            return False

        if self._today_production_kwh == value:
            return False

        self._today_production_kwh = value
        _LOGGER.debug("Forecast.Solar production today updated: %.2f", value)
        return True

    def _handle_tomorrow_production_change(self, entity_id, old_state, new_state) -> bool:
        try:
            value = float(new_state.state)
        except ValueError:
            _LOGGER.warning("Failed to parse Forecast.Solar production today from state: %s",
                            new_state.state)
            return False

        if self._tomorrow_production_kwh == value:
            return False

        self._tomorrow_production_kwh = value
        _LOGGER.debug("Forecast.Solar production now updated: %.2f", value)
        return True

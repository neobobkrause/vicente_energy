"""Base class for solar production forecast services."""

from abc import abstractmethod
from datetime import datetime
from typing import Optional
from .service import VEEntityStateChangeHandler, VEService


class ForecastService(VEService):
    """Provide solar production forecasts."""
    def __init__(self, hass,
                 entity_handlers: Optional[dict[str, VEEntityStateChangeHandler]] = None) -> None:
        """Initialize forecast storage attributes."""
        self._today_remaining_production_kwh: float = 0.0
        self._today_production_kwh: float = 0.0
        self._tomorrow_production_kwh: float = 0.0
        self._current_production_kw: float = 0.0

        super().__init__(hass, entity_handlers)

    def get_today_remaining_production_kwh(self) -> float:
        return self._today_remaining_production_kwh

    def get_today_production_kwh(self) -> float:
        return self._today_production_kwh

    def get_tomorrow_production_kwh(self) -> float:
        return self._tomorrow_production_kwh

    def get_current_production_kw(self) -> float:
        return self._current_production_kw

    def get_this_hour_production_kwh(self) -> float:
        current_hour = datetime.now().hour  # 0 through 23
        return self._get_today_hour_production_kwh(current_hour)

    def get_next_hour_production_kwh(self) -> float:
        current_hour = datetime.now().hour  # 0 through 23
        if current_hour == 23:
            return self._get_tomorrow_hour_production_kwh(0)

        return self._get_today_hour_production_kwh(current_hour+1)

    @abstractmethod
    def _get_today_hour_production_kwh(self, hour: int) -> float:
        pass

    @abstractmethod
    def _get_tomorrow_hour_production_kwh(self, hour: int) -> float:
        pass

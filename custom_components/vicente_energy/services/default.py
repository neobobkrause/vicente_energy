"""Fallback service implementations used when no real service is configured."""
from .forecast_service import ForecastService
from homeassistant.core import HomeAssistant

from .grid_service import GridService
from .ev_charger_service import EVChargerService, convert_amps_to_kw
from .battery_service import BatteryService
from .solar_service import SolarService


class DefaultEVChargerService(EVChargerService):
    """Simple charger service that stores power values locally."""

    def __init__(self, hass: HomeAssistant) -> None:
        super().__init__(hass)

    async def set_charging_power_amps(self, power_amps: int) -> None:
        self._charging_power_kw = convert_amps_to_kw(power_amps)

    async def set_charging_power_kw(self, power_kw: float) -> None:
        self._charging_power_kw = power_kw

class DefaultBatteryService(BatteryService):
    """Battery service with no external API."""

    def __init__(self, hass: HomeAssistant) -> None:
        super().__init__(hass)

class DefaultSolarService(SolarService):
    """Solar production service returning zeros."""

    def __init__(self, hass: HomeAssistant) -> None:
        super().__init__(hass)

class DefaultForecastService(ForecastService):
    """Use Solcast sensors to provide forecast data."""

    def __init__(self, hass: HomeAssistant) -> None:
        super().__init__(hass)

class DefaultGridService(GridService):
    """Basic grid service storing latest readings only."""

    def __init__(self, hass: HomeAssistant) -> None:
        super().__init__(hass)

"""Fallback service implementations used when no real service is configured."""

from typing import Optional

from homeassistant.core import HomeAssistant

from .ev_charger_service import EVChargerService
from .grid_service import GridService
from .ev_charger_service import convert_amps_to_kw

from .battery_service import BatteryService
from .solar_service import SolarService


class DefaultChargerService(EVChargerService):
    """Simple charger service that stores power values locally."""

    def __init__(self, hass: Optional[HomeAssistant]) -> None:
        """Initialize with the Home Assistant instance."""
        super().__init__(hass, None)

    async def set_charging_power_amps(self, power_amps: int) -> None:
        """Store the requested charging power in kW."""
        self._charging_power_kw = convert_amps_to_kw(power_amps)

    async def set_charging_power_kw(self, power_kw: float) -> None:
        """Set charging power directly in kW."""
        self._charging_power_kw = power_kw

class DefaultBatteryService(BatteryService):
    """Battery service with no external API."""

    def __init__(self, hass: Optional[HomeAssistant]) -> None:
        """Initialize the default battery service."""
        super().__init__(hass, None)

class DefaultSolarService(SolarService):
    """Solar production service returning zeros."""

    def __init__(self, hass: Optional[HomeAssistant]) -> None:
        """Initialize the default solar service."""
        super().__init__(hass, None)

class DefaultGridService(GridService):
    """Basic grid service storing latest readings only."""

    def __init__(self, hass: Optional[HomeAssistant]) -> None:
        """Initialize the grid service with no external dependency."""
        super().__init__(hass, None)



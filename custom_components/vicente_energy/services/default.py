"""Fallback service implementations used when no real service is configured."""

from typing import Optional

from homeassistant.core import HomeAssistant

from .battery_service import BatteryService
from .solar_service import SolarService


class DefaultChargerService(EVChargerService):
    """Simple charger service that stores power values locally."""

    def __init__(self, hass: Optional[HomeAssistant]) -> None:
        super().__init__(hass, None)

    async def set_charging_power_amps(self, power_amps: int) -> None:
        self._charging_power_kw = convert_amps_to_kw(power_amps)

    async def set_charging_power_kw(self, power_kw: float) -> None:
        self._charging_power_kw = power_kw

class DefaultBatteryService(BatteryService):
    """Battery service with no external API."""

    def __init__(self, hass: Optional[HomeAssistant]) -> None:
        super().__init__(hass, None)

class DefaultSolarService(SolarService):
    """Solar production service returning zeros."""

    def __init__(self, hass: Optional[HomeAssistant]) -> None:
        super().__init__(hass, None)

class DefaultGridService(GridService):
    """Basic grid service storing latest readings only."""

    def __init__(self, hass: Optional[HomeAssistant]) -> None:
        super().__init__(hass, None)

class DefaultGridService(GridService):
    def __init__(self, hass: Optional[HomeAssistant]) -> None:
        super().__init__(hass, None)


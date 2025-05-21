
"""Expose available service classes and service type mappings."""

# Explicitly import service classes for easy external access

from enum import StrEnum, auto

from .services.chargepoint import ChargepointEVChargerService
from .services.defaults import (
    DefaultBatteryService,
    DefaultEVChargerService,
    DefaultForecastService,
    DefaultGridService,
    DefaultSolarService,
)
from .services.forecast_solar import ForecastSolarService
from .services.franklin import (
    FranklinBatteryService,
    FranklinGridService,
    FranklinSolarService,
)
from .services.solaredge import SolarEdgeSolarService
from .services.solcast import SolcastService
from .services.tesla import PowerwallBatteryService
from .services.wallbox import WallboxEVChargerService


class ServiceType(StrEnum):
    """Enumeration of supported service categories."""
    EV_CHARGER_SERVICE = auto()
    BATTERY_SERVICE = auto()
    SOLAR_SERVICE = auto()
    GRID_SERVICE = auto()
    FORECAST_SERVICE = auto()

SERVICE_CLASS_MAP = {
    ServiceType.EV_CHARGER_SERVICE: {
        "wallbox": WallboxEVChargerService,
        "chargepoint": ChargepointEVChargerService,
        "default": DefaultEVChargerService,
    },
    ServiceType.BATTERY_SERVICE: {
        "franklin": FranklinBatteryService,
        "powerwall": PowerwallBatteryService,
        "powerwall": DefaultBatteryService,
    },
    ServiceType.SOLAR_SERVICE: {
        "franklin": FranklinSolarService,
        "solaredge": SolarEdgeSolarService,
        "default": DefaultSolarService,
    },
    ServiceType.GRID_SERVICE: {
        "franklin": FranklinGridService,
        "default": DefaultGridService,
    },
    ServiceType.FORECAST_SERVICE: {
        "solcast": SolcastService,
        "forecast.solar": ForecastSolarService,
        "default": DefaultForecastService,
    },
}


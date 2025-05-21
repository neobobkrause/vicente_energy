
"""Expose available service classes and service type mappings."""

# Explicitly import service classes for easy external access

from enum import StrEnum, auto

from .chargepoint import ChargepointEVChargerService
from .default import (
    DefaultBatteryService,
    DefaultEVChargerService,
    DefaultForecastService,
    DefaultGridService,
    DefaultSolarService,
)
from .forecast_solar import ForecastSolarService
from .franklin import (
    FranklinBatteryService,
    FranklinGridService,
    FranklinSolarService,
)
from .solaredge import SolarEdgeSolarService
from .solcast import SolcastService
from .tesla import PowerwallBatteryService
from .wallbox import WallboxEVChargerService


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
        "default": DefaultBatteryService,
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

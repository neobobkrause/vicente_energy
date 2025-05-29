"""Expose available service classes and service type mappings."""

# Explicitly import service classes for easy external access

from enum import StrEnum, auto

from .budget_service import ChargingBudgetService
from .charging_session_service import ChargingSessionService
from .default import (
    DefaultBatteryService,
    DefaultEVChargerService,
    DefaultForecastService,
    DefaultGridService,
    DefaultSolarService,
)

from .chargepoint import ChargepointEVChargerService
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
    BUDGET_SERVICE = auto()
    CHARGING_SERVICE = auto()

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
    ServiceType.BUDGET_SERVICE: {
        "default": ChargingBudgetService,
    },
    ServiceType.CHARGING_SERVICE: {
        "default": ChargingSessionService,
    },
}

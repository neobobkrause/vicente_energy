
"""Dataclass models used throughout the Vicente Energy integration."""

from dataclasses import dataclass
from typing import List


@dataclass
class Signals:
    """Snapshot of sensor inputs used for calculations."""
    solar_power_w: float
    battery_soc_pct: float
    house_load_total_w: float
    wallbox_power_w: float
    agate_inverter_on: bool

@dataclass
class Forecasts:
    """Hourly solar and load forecast collections."""
    solar_24h_kwh: List[float]
    load_24h_kwh: List[float]

@dataclass
class SessionEstimates:
    """Estimated values for a potential charging session."""
    kwh_estimated: float
    soc_end_pct: float
    available_after_kwh: float

@dataclass
class SessionActuals:
    """Actual values recorded from a finished session."""
    kwh_used: float

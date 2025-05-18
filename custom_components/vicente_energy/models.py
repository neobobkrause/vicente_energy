
from dataclasses import dataclass
from typing import List


@dataclass
class Signals:
    solar_power_w: float
    battery_soc_pct: float
    house_load_total_w: float
    wallbox_power_w: float
    agate_inverter_on: bool

@dataclass
class Forecasts:
    solar_24h_kwh: List[float]
    load_24h_kwh: List[float]

@dataclass
class SessionEstimates:
    kwh_estimated: float
    soc_end_pct: float
    available_after_kwh: float

@dataclass
class SessionActuals:
    kwh_used: float

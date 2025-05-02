from dataclasses import dataclass
from typing import List

@dataclass
class Signals:
    solar_power_w: float
    battery_soc_pct: float
    house_load_total_w: float
    wallbox_power_w: float
    agate_inverter_on: bool

    @property
    def house_load_no_charger(self) -> float:
        return self.house_load_total_w - self.wallbox_power_w

@dataclass
class Forecasts:
    solar_24h_kwh: List[float]
    load_24h_kwh: List[float]

@dataclass
class SessionActuals:
    kwh_used: float

@dataclass
class SessionEstimates:
    kwh_estimated: float
    soc_end_pct: float
    available_after_kwh: float

class ChargeEstimator:
    def __init__(self, params, state_manager):
        """Initialize with user parameters and a state manager instance."""
        self.params = params
        self.state = state_manager

    def compute_24h_budget(self, forecasts: Forecasts, signals: Signals) -> float:
        """Compute kWh available for the next 24h using corrected forecasts and current state."""
        raise NotImplementedError

    def compute_power_level(self, signals: Signals, budget_remaining: float) -> float:
        """Compute kW charging rate given current signals and remaining budget."""
        raise NotImplementedError

    def compute_session_estimates(self, signals: Signals, duration_minutes: int) -> SessionEstimates:
        """Estimate session energy, end-of-session SOC, and leftover budget."""
        raise NotImplementedError

    def learn_session(self, actuals: SessionActuals) -> None:
        """Update internal biases based on actual vs. estimated session data."""
        raise NotImplementedError
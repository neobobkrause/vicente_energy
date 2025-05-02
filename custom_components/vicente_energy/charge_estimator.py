import logging
from .models import Signals, Forecasts, SessionEstimates, SessionActuals
from .state_manager import StateManager
from typing import Dict

_LOGGER = logging.getLogger(__name__)

class ChargeEstimator:
    def __init__(self, params: Dict, state_manager: StateManager):
        self.params = params
        self.state = state_manager
        self.capacity = params.get("battery_capacity_kwh", 10.0)
        self.reserve = params.get("reserve_soc_pct", 20.0)
        self.efficiency = params.get("storage_efficiency", 0.9)
        self.max_power = params.get("max_charger_power_kw", 7.4)
        self.session_alpha = params.get("session_learning_alpha", 0.1)
        self._last_raw_kwh = None

    def compute_24h_budget(self, forecasts: Forecasts, signals: Signals) -> float:
        total_solar = sum(forecasts.solar_24h_kwh)
        total_load = sum(forecasts.load_24h_kwh)
        battery_avail = max(
            0.0,
            (signals.battery_soc_pct / 100 - self.reserve / 100)
            * self.capacity * self.efficiency
        )
        budget = max(0.0, total_solar - total_load + battery_avail)
        _LOGGER.debug(
            "24h budget: solar=%.2f, load=%.2f, batt_avail=%.2f -> budget=%.2f",
            total_solar, total_load, battery_avail, budget
        )
        return budget

    def compute_power_level(self, signals: Signals, budget_remaining: float) -> float:
        solar_kw = signals.solar_power_w / 1000
        load_kw = signals.house_load_total_w / 1000

        if not signals.agate_inverter_on:
            direct = 0.0
        else:
            direct = max(0.0, solar_kw - load_kw)

        if direct > 0:
            power = min(direct, self.max_power, budget_remaining)
        else:
            soc_above = max(0.0, signals.battery_soc_pct - self.reserve) / 100
            if soc_above > 0:
                batt_kwh = soc_above * self.capacity * self.efficiency
                power = min(batt_kwh, self.max_power, budget_remaining)
            else:
                power = 0.0

        _LOGGER.debug("Power level: direct=%.2f kW, power=%.2f kW", direct, power)
        return power

    def compute_session_estimates(self, signals: Signals, duration_minutes: int) -> SessionEstimates:
        budget = self.compute_24h_budget(Forecasts([], []), signals)
        power = self.compute_power_level(signals, budget)
        raw_kwh = power * (duration_minutes / 60)
        self._last_raw_kwh = raw_kwh

        bias = self.state.get_session_bias()
        est_kwh = raw_kwh * (1 + bias)
        soc_drop_pct = (est_kwh / self.capacity) * 100
        soc_end = max(self.reserve, signals.battery_soc_pct - soc_drop_pct)
        avail_after = max(0.0, budget - est_kwh)

        return SessionEstimates(
            kwh_estimated=est_kwh,
            soc_end_pct=soc_end,
            available_after_kwh=avail_after
        )

    def learn_session(self, actuals: SessionActuals) -> None:
        prev_bias = self.state.get_session_bias()
        alpha = self.session_alpha
        raw = self._last_raw_kwh if self._last_raw_kwh is not None else 0.0

        if raw > 0:
            error = (actuals.kwh_used - raw) / raw
        else:
            error = 1.0

        new_bias = alpha * error + (1 - alpha) * prev_bias
        self.state.update_session_bias(new_bias, raw_kwh=raw)
        _LOGGER.info(
            "Session learning: raw=%.3f, actual=%.3f, error=%.3f, new_bias=%.3f",
            raw, actuals.kwh_used, error, new_bias
        )
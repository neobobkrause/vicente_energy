from .const import CONF_SESSION_LEARNING_ALPHA
from .models import Forecasts, Signals


class ChargeEstimator:
    def __init__(self, params: dict, state_manager):
        self._params = params
        self._state_manager = state_manager

    def estimate(self, fc, sig):
        """Bridge method for hourly_update_method in __init__.py."""
        return self.compute_24h_budget(fc, sig)

    def compute_24h_budget(self, fc: Forecasts, sig: Signals) -> float:
        """Compute 24 h charging budget (kWh)."""
        total_solar = sum(fc.solar_24h_kwh)
        total_load = sum(fc.load_24h_kwh)
        solar_net = total_solar - total_load
        solar_budget = max(solar_net, 0.0)

        soc_frac = sig.battery_soc_pct / 100.0
        reserve_frac = self._params.get('reserve_soc_pct', 0.0) / 100.0
        cap = self._params.get('battery_capacity_kwh', 0.0)
        eff = self._params.get('storage_efficiency', 1.0)

        # No battery draw if at or above 100% SOC
        if sig.battery_soc_pct >= 100.0:
            batt_budget = 0.0
        else:
            batt_budget = max(soc_frac - reserve_frac, 0.0) * cap * eff

        return solar_budget + batt_budget

    def compute_power_level(self, sig: Signals, budget_remaining: float) -> float:
        """Compute desired charge power (kW) based on solar or battery."""
        # Inverter off => no charging
        if not sig.agate_inverter_on:
            return 0.0

        solar_surplus_kw = max((sig.solar_power_w - sig.house_load_total_w) / 1000.0, 0.0)
        max_power = self._params.get('max_charger_power_kw', 0.0)

        # Solar-first
        if solar_surplus_kw > 0:
            return min(solar_surplus_kw, max_power, budget_remaining)

        # Battery draw scenario
        soc_frac = sig.battery_soc_pct / 100.0
        reserve_frac = self._params.get('reserve_soc_pct', 0.0) / 100.0
        cap = self._params.get('battery_capacity_kwh', 0.0)
        eff = self._params.get('storage_efficiency', 1.0)

        batt_kwh = max(soc_frac - reserve_frac, 0.0) * cap * eff
        return min(batt_kwh, max_power, budget_remaining)

    async def learn_session(self, actual):
        """Incorporate the results of a finished charging session to adjust bias."""
        # Accept either SessionActuals or a numeric kWh
        actual_kwh = actual.kwh_used if hasattr(actual, "kwh_used") else float(actual)
        estimated_kwh = self._estimate_session_kwh()
        # Compute error = actual usage – estimated usage
        error = actual_kwh - estimated_kwh
        # Learning rate (alpha) for session bias
        alpha = self._params.get(CONF_SESSION_LEARNING_ALPHA, 0.1)
        # Update session bias in state manager
        await self._state_manager.update_session_bias(alpha, actual_kwh)
        # Persist the updated bias asynchronously
        try:
            self._state_manager.hass.async_create_task(self._state_manager.async_save())
        except AttributeError:
            import asyncio
            asyncio.create_task(self._state_manager.async_save())

    def _estimate_session_kwh(self):
        """Estimate expected kWh for the next session based on history."""
        last_kwh = self._state_manager.data.get("last_raw_session_kwh")
        if last_kwh is not None:
            try:
                return float(last_kwh)
            except (ValueError, TypeError):
                return 0.0
        return 0.0

    def _estimate_session_kwh(self):
        # Implement this method explicitly according to your actual estimation logic.
        return 0.0  # Explicit placeholder implementation

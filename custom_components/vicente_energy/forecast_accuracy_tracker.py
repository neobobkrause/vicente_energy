import logging
from .state_manager import StateManager

_LOGGER = logging.getLogger(__name__)

class ForecastAccuracyTracker:
    """
    Tracks forecast error history and applies simple exponential smoothing.
    """
    def __init__(self, state_manager: StateManager, alpha: float = 0.2):
        self.state = state_manager
        self.alpha = alpha

    def update_solar(self, forecast_kwh: float, actual_kwh: float):
        error = (actual_kwh - forecast_kwh) / forecast_kwh if forecast_kwh else 0.0
        prev_bias = self.state.get_solar_bias()
        new_bias = self.alpha * error + (1 - self.alpha) * prev_bias
        self.state.update_solar_bias(new_bias)
        _LOGGER.debug(
            "Solar bias updated: alpha=%s, error=%s, bias=%s",
            self.alpha, error, new_bias
        )

    def update_load(self, forecast_kwh: float, actual_kwh: float):
        error = (actual_kwh - forecast_kwh) / forecast_kwh if forecast_kwh else 0.0
        prev_bias = self.state.get_load_bias()
        new_bias = self.alpha * error + (1 - self.alpha) * prev_bias
        self.state.update_load_bias(new_bias)
        _LOGGER.debug(
            "Load bias updated: alpha=%s, error=%s, bias=%s",
            self.alpha, error, new_bias
        )
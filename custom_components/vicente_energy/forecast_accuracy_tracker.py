from .state_manager import StateManager


class ForecastAccuracyTracker:
    def __init__(self, state_manager: StateManager, alpha: float, state: StateManager = None):
        self._state = state if state is not None else state_manager
        self._alpha = alpha

    def update_solar(self, forecast_kwh: float, actual_kwh: float):
        if forecast_kwh == 0:
            return
        error = (actual_kwh - forecast_kwh) / forecast_kwh
        new_bias = error * self._alpha
        self._state.update_solar_bias(new_bias)

    def update_load(self, forecast_kwh: float, actual_kwh: float):
        if forecast_kwh == 0:
            return
        error = (actual_kwh - forecast_kwh) / forecast_kwh
        new_bias = error * self._alpha
        self._state.update_load_bias(new_bias)

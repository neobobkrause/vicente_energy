"""Maintains historical load data and applies bias for next-day forecasting."""

import logging
from collections import deque
from typing import List
from .state_manager import StateManager

_LOGGER = logging.getLogger(__name__)

class LoadForecaster:
    """
    Simple load forecaster using past N hourly values.
    Pads forecast to length 24 and applies bias from StateManager.
    """
    def __init__(self, state_manager: StateManager, window: int = 24):
        self.state = state_manager
        self.history = deque(maxlen=window)

    def update_history(self, actual_load_kwh: float) -> None:
        """Add an actual hourly load reading to history."""
        self.history.append(actual_load_kwh)

    def get_corrected_forecast(self) -> List[float]:
        """Return a 24-hour forecast, padded with zeros, then apply load_bias."""
        raw = [0.0] * (self.history.maxlen - len(self.history)) + list(self.history)
        bias = self.state.get_load_bias()
        corrected = [value * (1 + bias) for value in raw]
        _LOGGER.debug("Load forecast raw=%s bias=%.3f corrected=%s", raw, bias, corrected)
        return corrected
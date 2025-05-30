"""Simple load forecasting based on recent history."""

from collections import deque

from .const import CONF_HOUSE_LOAD_ENTITY


class LoadForecaster:
    """Forecast house load using a rolling history window."""

    def __init__(self, hass, config, state_manager):
        """Initialize with Home Assistant handle and state manager."""
        self.hass = hass
        self.entity_id = config.get(CONF_HOUSE_LOAD_ENTITY)
        self.state = state_manager
        self.history = deque(maxlen=24)  # Stores last 24 hourly values

    def update_history(self, actual_value):
        """Append the latest measured value to the history buffer."""
        if actual_value is not None:
            try:
                val = float(actual_value)
                self.history.append(val)
            except ValueError:
                pass

    def get_raw_forecast(self):
        """Return the last 24 readings or zero if no history."""
        # If no history, predict zero for 24 hours
        if len(self.history) == 0:
            return [0.0] * 24
        values = list(self.history)
        if len(values) < 24:
            # Pad the beginning with zeros if history is shorter than 24 hours
            return [0.0] * (24 - len(values)) + values
        else:
            # Use last 24 recorded values
            return values[-24:]

    def get_corrected_forecast(self):
        """Apply stored bias to the raw forecast."""
        raw = self.get_raw_forecast()
        bias = self.state.get_load_bias()
        return [max(val * (1 + bias), 0.0) for val in raw]


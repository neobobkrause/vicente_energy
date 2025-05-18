from homeassistant.helpers.storage import Store


class StateManager:

    def __init__(self, hass, entry_id):
        self.hass = hass
        self.entry_id = entry_id
        self._store = Store(hass, f"vicente_energy_{entry_id}", f"vicente_energy_{entry_id}.json")
        self.data = {
            "solar_bias": 0.0,
            "load_bias": 0.0,
            "last_raw_session_kwh": None,
            "session_bias": 0.0,
            "last_session_kwh": 0.0,
            "forecast_error_history": {"solar_errors": [], "load_errors": []},
            "session_bias_history": []
        }

    def update_solar_bias(self, bias: float):
        self.data['solar_bias'] = bias

    def update_load_bias(self, bias: float):
        self.data['load_bias'] = bias

    def get_load_bias(self) -> float:
        return self.data.get('load_bias', 0.0)

    def get_session_bias(self) -> float:
        return self.data.get('session_bias', 0.0)

    async def async_load(self):
        stored = await self._store.async_load()
        if stored:
            self.data.update(stored)

    async def async_save(self):
        await self._store.async_save(self.data)

    async def update_session_bias(self, alpha: float, actual_kwh: float):
        current_bias = self.data.get('session_bias', 0.0)
        new_bias = current_bias + alpha * (actual_kwh - current_bias)
        self.data['session_bias'] = new_bias
        self.data['last_raw_session_kwh'] = actual_kwh
        self.data['session_bias_history'].append(actual_kwh)
        await self.async_save()

    async def set_session_bias(self, bias_value: float):
        self.data['session_bias'] = bias_value
        await self.async_save()

    def record_forecast_error(self, forecast_type: str, error_value: float):
        """Append a forecast error for solar or load bias tracking."""
        history = self.data.setdefault('forecast_error_history', {'solar_errors': [], 'load_errors': []})
        history[f"{forecast_type}_errors"].append(error_value)

    # New methods:
    async def learn_session_bias(self, actual_kwh: float, estimated_kwh: float):
        """Alternative method to update session bias directly using actual vs estimated (called by SessionManager)."""
        error = actual_kwh - estimated_kwh
        alpha = self.data.get('session_learning_alpha', 0.1)
        current_bias = self.data.get('session_bias', 0.0)
        new_bias = current_bias + alpha * (error - current_bias)
        self.data['session_bias'] = new_bias
        self.data['last_raw_session_kwh'] = actual_kwh
        self.data['session_bias_history'].append(actual_kwh)
        await self.async_save()

    async def save_last_session_kwh(self, kwh: float):
        """Record the last completed session's kWh usage."""
        self.data['last_session_kwh'] = kwh
        await self.async_save()

    async def reset_history(self):
        """Reset all stored biases and history to defaults."""
        self.data['solar_bias'] = 0.0
        self.data['load_bias'] = 0.0
        self.data['session_bias'] = 0.0
        self.data['last_session_kwh'] = 0.0
        self.data['last_raw_session_kwh'] = None
        self.data['forecast_error_history'] = {'solar_errors': [], 'load_errors': []}
        self.data['session_bias_history'] = []
        await self.async_save()

    def get_solar_bias(self) -> float:
        return self.data.get('solar_bias', 0.0)

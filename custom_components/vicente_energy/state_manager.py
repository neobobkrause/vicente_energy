import logging
from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

_LOGGER = logging.getLogger(__name__)
STORAGE_KEY = "vicente_energy_state"
STORAGE_VERSION = 3  # bumped for forecast error history

class StateManager:
    """
    Persists biases and error histories using Home Assistant storage helper.
    Schema version 3 includes:
      - solar_bias, load_bias, session_bias
      - session_bias_history
      - last_raw_session_kwh
      - forecast_error_history with 'solar_errors' and 'load_errors'
    """
    def __init__(self, hass: HomeAssistant):
        self.hass = hass
        self.store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self.data = {
            "solar_bias": 0.0,
            "load_bias": 0.0,
            "session_bias": 0.0,
            "session_bias_history": [],
            "last_raw_session_kwh": None,
            "forecast_error_history": {
                "solar_errors": [],
                "load_errors": []
            },
        }

    async def async_load(self):
        stored = await self.store.async_load()
        if stored:
            for key, default in self.data.items():
                self.data[key] = stored.get(key, default)
            _LOGGER.debug("Loaded persisted state (v3): %s", self.data)

    async def async_save(self):
        await self.store.async_save(self.data)
        _LOGGER.debug("Saved state (v3): %s", self.data)

    def get_solar_bias(self) -> float:
        return self.data.get("solar_bias", 0.0)

    def get_load_bias(self) -> float:
        return self.data.get("load_bias", 0.0)

    def get_session_bias(self) -> float:
        return self.data.get("session_bias", 0.0)

    def update_solar_bias(self, bias: float):
        self.data["solar_bias"] = bias
        try:
            self.hass.async_create_task(self.async_save())
        except AttributeError:
            pass

    def update_load_bias(self, bias: float):
        self.data["load_bias"] = bias
        try:
            self.hass.async_create_task(self.async_save())
        except AttributeError:
            pass

    def update_session_bias(self, bias: float, raw_kwh: float = None):
        self.data["session_bias"] = bias
        self.data.setdefault("session_bias_history", []).append(bias)
        if raw_kwh is not None:
            self.data["last_raw_session_kwh"] = raw_kwh
        try:
            self.hass.async_create_task(self.async_save())
        except AttributeError:
            pass

    def record_forecast_error(self, category: str, error: float):
        key = f"{category}_errors"
        hist = self.data.setdefault("forecast_error_history", {}).setdefault(key, [])
        hist.append(error)
        try:
            self.hass.async_create_task(self.async_save())
        except AttributeError:
            pass
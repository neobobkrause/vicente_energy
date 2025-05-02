import logging
from typing import Any, List, Union
from datetime import datetime, timedelta
from homeassistant.core import HomeAssistant
from .state_manager import StateManager

_LOGGER = logging.getLogger(__name__)

class SolarForecastAdapter:
    """
    Reads solar forecasts from HA entities and applies stored bias.
    Supports Solcast PV Forecast sensor with 'forecast' attribute list of dicts.
    """
    def __init__(self, hass: HomeAssistant, solar_entities: List[str], state_manager: StateManager):
        self.hass = hass
        self._solar_forecast_entities = solar_entities
        self.state_manager = state_manager

    def get_corrected_forecast(self) -> List[float]:
        raw = self._fetch_raw_forecast()
        bias = self.state_manager.get_solar_bias()
        corrected = [v * (1 + bias) for v in raw]
        return corrected

    def _fetch_raw_forecast(self) -> List[float]:
        """
        If exactly one entity is configured, assume Solcast:
        pull its 'forecast' attribute list which can contain dict entries
        with 'pv_estimate' per period (kWh). Collapse half-hourly into 24-hour kWh.
        Otherwise fall back to reading each entity.state as float.
        """
        entities = self._solar_forecast_entities
        if len(entities) == 1:
            ent = entities[0]
            state = self.hass.states.get(ent)
            attr = getattr(state, 'attributes', {}).get("forecast")
            if isinstance(attr, list) and len(attr) > 0:
                # Determine if list of dicts
                if isinstance(attr[0], dict):
                    values = []
                    for entry in attr:
                        try:
                            # 'pv_estimate' is kWh for the period
                            pv = float(entry.get("pv_estimate", 0.0))
                        except Exception:
                            pv = 0.0
                        values.append(pv)
                else:
                    # list of raw numbers
                    values = [float(x) if isinstance(x, (int, float, str)) else 0.0 for x in attr]

                n = len(values)
                # collapse 48 half-hour entries into 24 hourly sums
                if n == 48:
                    hourly = [values[i] + values[i+1] for i in range(0, 48, 2)]
                elif n == 24:
                    hourly = values
                else:
                    _LOGGER.error("Solcast forecast length %d unsupported; expect 24 or 48", n)
                    hourly = [0.0] * 24
                return hourly

        # Fallback path: direct state->float per entity
        raw = []
        for ent in entities:
            st = self.hass.states.get(ent)
            try:
                raw.append(float(st.state))
            except Exception:
                raw.append(0.0)
        # Pad/truncate to 24
        if len(raw) < 24:
            raw = raw + [0.0] * (24 - len(raw))
        elif len(raw) > 24:
            raw = raw[:24]
        return raw
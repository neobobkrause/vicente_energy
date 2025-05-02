from homeassistant.core import HomeAssistant
from typing import List
import datetime

from .const import SIGNAL_HISTORY_LENGTH

class InputCollector:
    def __init__(
        self,
        hass: HomeAssistant,
        solar_power_entity: str,
        forecast_entities: List[str],
        battery_soc_entity: str,
        house_load_entity: str,
        wallbox_power_entity: str,
        inverter_on_entity: str,
        wallbox_state_entity: str,
        battery_capacity_kwh: float,
        reserve_soc_pct: float,
        storage_efficiency: float,
        max_charger_power_kw: float,
        session_learning_alpha: float,
        budget_update_interval_hours: int,
        update_interval_minutes: int,
    ):
        self.hass = hass
        self.solar_entity = solar_power_entity
        self.forecast_entities = forecast_entities
        self.battery_soc_entity = battery_soc_entity
        self.house_load_entity = house_load_entity
        self.wallbox_power_entity = wallbox_power_entity
        self.inverter_on_entity = inverter_on_entity
        self.wallbox_state_entity = wallbox_state_entity

        # New parameters
        self.battery_capacity_kwh = battery_capacity_kwh
        self.reserve_soc_pct = reserve_soc_pct
        self.storage_efficiency = storage_efficiency
        self.max_charger_power_kw = max_charger_power_kw
        self.session_learning_alpha = session_learning_alpha

        # Intervals
        self.budget_update_interval = datetime.timedelta(hours=budget_update_interval_hours)
        self.update_interval = datetime.timedelta(minutes=update_interval_minutes)

        # History buffer
        self.signal_history = []

    def get_signals(self):
        """Collects current state/signals for forecasting and estimation."""
        # Example implementation using state lookups
        solar = self.hass.states.get(self.solar_entity)
        solar_power = float(solar.state) if solar and solar.state is not None else 0.0

        battery = self.hass.states.get(self.battery_soc_entity)
        soc_pct = float(battery.state) if battery and battery.state is not None else 0.0

        house = self.hass.states.get(self.house_load_entity)
        house_load = float(house.state) if house and house.state is not None else 0.0

        wallbox = self.hass.states.get(self.wallbox_power_entity)
        wallbox_power = float(wallbox.state) if wallbox and wallbox.state is not None else 0.0

        inverter = self.hass.states.get(self.inverter_on_entity)
        inverter_on = bool(inverter and inverter.state in ["on", "true", "1", True])

        # Smoothing / history maintenance (simplified)
        self.signal_history.append(solar_power)
        if len(self.signal_history) > SIGNAL_HISTORY_LENGTH:
            self.signal_history.pop(0)
        solar_smoothed = sum(self.signal_history) / len(self.signal_history)

        return {
            "solar_power_w": solar_smoothed,
            "battery_soc_pct": soc_pct,
            "house_load_w": house_load,
            "wallbox_power_w": wallbox_power,
            "inverter_on": inverter_on,
        }

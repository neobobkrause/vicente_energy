"""Service implementations for Powerwall devices."""

import logging
from homeassistant.core import HomeAssistant

from .battery_service import CONF_BATTERY_RESERVE, BatteryService
from .service import VEEntityStateChangeHandler

_LOGGER = logging.getLogger(__name__)

class PowerwallBatteryService(BatteryService):
    """Battery service for Tesla Powerwall systems."""


    def __init__(self, hass: HomeAssistant) -> None:
        self._battery_reserve: int = 20  # 0–100

        # Define handlers
        handlers: dict[str, VEEntityStateChangeHandler] = {
            "sensor.battery_reserve": self._handle_reserve_change,
            "sensor.battery_capacity": self._handle_soc_change,
            "sensor.battery_import": self._handle_today_charge_change,
            "sensor.battery_export": self._handle_today_discharge_change,
        }
        super().__init__(hass, handlers)

    def _handle_soc_change(self, _entity_id, _old_state, new_state) -> bool:
        try:
            value = float(new_state.state)
        except ValueError:
            _LOGGER.warning("Failed to parse Powerwall SOC from state: %s", new_state.state)
            return False

        if self._battery_soc == value:
            return False

        self._battery_soc = value
        _LOGGER.debug("Powerwall SOC updated: %.1f%%", value)
        return True

    def _handle_reserve_change(self, _entity_id, old_state, new_state) -> bool:
        try:
            value = int(new_state.state)
        except ValueError:
            _LOGGER.warning("Failed to parse Powerwall reserve from state: %s", new_state.state)
            return False

        if self._battery_reserve == value:
            return False

        self._battery_reserve = value

        # Notify subscribers using the VE battery vendor independent entity_id
        self._notify_subscribers(CONF_BATTERY_RESERVE, old_state, new_state)
        _LOGGER.debug("Powerwall reserve updated: %.1f%%", value)
        return True

    def _handle_today_charge_change(self, _entity_id, _old_state, new_state) -> bool:
        try:
            value = float(new_state.state)
        except ValueError:
            _LOGGER.warning("Failed to parse Powerwall charge energy: %s", new_state.state)
            return False

        if self._today_charge_kwh == value:
            return False

        self._today_charge_kwh = value
        _LOGGER.debug("Today's Powerwall charge updated: %.2f kWh", value)
        return True

    def _handle_today_discharge_change(self, _entity_id, _old_state, new_state) -> bool:
        try:
            value = float(new_state.state)
        except ValueError:
            _LOGGER.warning("Failed to parse Powerwall discharge energy: %s", new_state.state)
            return False

        if self._today_discharge_kwh == value:
            return False

        self._today_discharge_kwh = value
        _LOGGER.debug("Today's Powerwall discharge updated: %.2f kWh", value)
        return True

"""Service implementations for SolarEdge devices."""

import logging
from homeassistant.core import HomeAssistant

from .grid_service import GridService
from .battery_service import BatteryService
from .service import VEEntityStateChangeHandler
from .solar_service import SolarService

_LOGGER = logging.getLogger(__name__)

class SolarEdgeSolarService(SolarService):
    """Solar production service for SolarEdge inverters through the local MODBUS interface."""

    def __init__(self, hass: HomeAssistant) -> None:
        # Define handlers
        handlers: dict[str, VEEntityStateChangeHandler] = {
            "sensor.solaredge_ac_power": self._handle_now_change,
            "sensor.solaredge_ac_energy_kwh": self._handle_today_change,
        }
        super().__init__(hass, handlers)

    def _handle_now_change(self, entity_id, old_state, new_state) -> bool:
        try:
            value = float(new_state.state)
        except ValueError:
            _LOGGER.warning("Failed to parse SolarEdge production now from state: %s",
                            new_state.state)
            return False

        if self._now_production_kw == value:
            return False

        self._now_production_kw = value
        _LOGGER.debug("SolarEdge production now updated: %.2f", value)
        return True

    def _handle_today_change(self, entity_id, old_state, new_state) -> bool:
        try:
            value = float(new_state.state)
        except ValueError:
            _LOGGER.warning("Failed to parse SolarEdge production today energy: %s", new_state.state)
            return False

        if self._today_production_kwh == value:
            return False

        self._today_production_kwh = value
        _LOGGER.debug("Today's SolarEdge production today updated: %.2f kWh", value)
        return True


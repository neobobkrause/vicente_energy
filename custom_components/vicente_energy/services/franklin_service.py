import logging

from .battery_service import BatteryService
from .service import VEEntityStateChangeHandler
from .solar_service import SolarService

_LOGGER = logging.getLogger(__name__)

class FranklinBatteryService(BatteryService):
    def __init__(self, hass):
        # Define handlers
        handlers: dict[str, VEEntityStateChangeHandler] = {
            "sensor.franklinwh_state_of_charge": self._handle_soc_change,
            "sensor.franklinwh_battery_charge": self._handle_today_charge_change,
            "sensor.franklinwh_battery_discharge": self._handle_today_discharge_change,
        }
        super().__init__(hass, handlers)

    def _handle_soc_change(self, entity_id, old_state, new_state) -> bool:
        if new_state.state not in ("unavailable", "unknown") and (old_state is None or new_state is not old_state):
            try:
                self._battery_soc = float(new_state.state)
                _LOGGER.debug("Franklin SOC updated: %.1f%%", self._battery_soc)

                return True
            except ValueError:
                _LOGGER.warning("Failed to parse Franklin SOC from state: %s", new_state.state)

        return False

    def _handle_today_charge_change(self, entity_id, old_state, new_state) -> bool:
        if new_state.state not in ("unavailable", "unknown") and (old_state is None or new_state is not old_state):
            try:
                self._today_charge_kwh = float(new_state.state)
                _LOGGER.debug("Today's Franklin charge updated: %.2f kWh", self._today_charge_kwh)

                return True
            except ValueError:
                _LOGGER.warning("Failed to parse Franklin charge energy: %s", new_state.state)

        return False

    def _handle_today_discharge_change(self, entity_id, old_state, new_state) -> bool:
        if new_state.state not in ("unavailable", "unknown") and (old_state is None or new_state is not old_state):
            try:
                self._today_discharge_kwh = float(new_state.state)
                _LOGGER.debug("Today's Franklin discharge updated: %.2f kWh", self._today_discharge_kwh)

                return True
            except ValueError:
                _LOGGER.warning("Failed to parse Franklin discharge energy: %s", new_state.state)

        return False


class FranklinSolarService(SolarService):
    def __init__(self, hass):
        # Define handlers
        handlers: dict[str, VEEntityStateChangeHandler] = {
            full("sensor.franklinwh_solar_energy"): self._handle_now_change,
            full("sensor.franklinwh_solar_production"): self._handle_today_change,
        }
        super().__init__(hass, handlers)

    def _handle_now_change(self, entity_id, old_state, new_state) -> bool:
        if new_state.state not in ("unavailable", "unknown") and (old_state is None or new_state is not old_state):
            try:
                self._now_production_kw = float(new_state.state)
                _LOGGER.debug("Franklin production now updated: %.2f", self._now_production_kw)

                return True
            except ValueError:
                _LOGGER.warning("Failed to parse Franklin production now from state: %s", new_state.state)

        return False

    def _handle_today_change(self, entity_id, old_state, new_state) -> bool:
        if new_state.state not in ("unavailable", "unknown") and (old_state is None or new_state is not old_state):
            try:
                self._today_production_kwh = float(new_state.state)
                _LOGGER.debug("Today's Franklin production today updated: %.2f kWh", self._today_production_kwh)

                return True
            except ValueError:
                _LOGGER.warning("Failed to parse Franklin production today energy: %s", new_state.state)

        return False


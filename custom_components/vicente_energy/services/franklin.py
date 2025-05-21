"""Service implementations for FranklinWH devices."""

import logging
from homeassistant.core import HomeAssistant

from .grid_service import GridService
from .battery_service import BatteryService
from .service import VEEntityStateChangeHandler
from .solar_service import SolarService

_LOGGER = logging.getLogger(__name__)

class FranklinBatteryService(BatteryService):
    """Battery service for FranklinWH systems."""

    def __init__(self, hass: HomeAssistant) -> None:
        # Define handlers
        handlers: dict[str, VEEntityStateChangeHandler] = {
            "sensor.franklinwh_state_of_charge": self._handle_soc_change,
            "sensor.franklinwh_battery_charge": self._handle_today_charge_change,
            "sensor.franklinwh_battery_discharge": self._handle_today_discharge_change,
        }
        super().__init__(hass, handlers)

    def _handle_soc_change(self, entity_id, old_state, new_state) -> bool:
        try:
            value = float(new_state.state)
        except ValueError:
            _LOGGER.warning("Failed to parse Franklin SOC from state: %s", new_state.state)
            return False

        if self._battery_soc == value:
            return False

        self._battery_soc = value
        _LOGGER.debug("Franklin SOC updated: %.1f%%", value)
        return True

    def _handle_today_charge_change(self, entity_id, old_state, new_state) -> bool:
        try:
            value = float(new_state.state)
        except ValueError:
            _LOGGER.warning("Failed to parse Franklin charge energy: %s", new_state.state)
            return False

        if self._today_charge_kwh == value:
            return False

        self._today_charge_kwh = value
        _LOGGER.debug("Today's Franklin charge updated: %.2f kWh", value)
        return True

    def _handle_today_discharge_change(self, entity_id, old_state, new_state) -> bool:
        try:
            value = float(new_state.state)
        except ValueError:
            _LOGGER.warning("Failed to parse Franklin discharge energy: %s", new_state.state)
            return False

        if self._today_discharge_kwh == value:
            return False

        self._today_discharge_kwh = value
        _LOGGER.debug("Today's Franklin discharge updated: %.2f kWh", value)
        return True

class FranklinSolarService(SolarService):
    """Solar production service for FranklinWH inverters."""

    def __init__(self, hass: HomeAssistant) -> None:
        # Define handlers
        handlers: dict[str, VEEntityStateChangeHandler] = {
            "sensor.franklinwh_solar_energy": self._handle_now_change,
            "sensor.franklinwh_solar_production": self._handle_today_change,
        }
        super().__init__(hass, handlers)

    def _handle_now_change(self, entity_id, old_state, new_state) -> bool:
        try:
            value = float(new_state.state)
        except ValueError:
            _LOGGER.warning("Failed to parse Franklin production now from state: %s",
                            new_state.state)
            return False

        if self._now_production_kw == value:
            return False

        self._now_production_kw = value
        _LOGGER.debug("Franklin production now updated: %.2f", value)
        return True

    def _handle_today_change(self, entity_id, old_state, new_state) -> bool:
        try:
            value = float(new_state.state)
        except ValueError:
            _LOGGER.warning("Failed to parse Franklin production today energy: %s", new_state.state)
            return False

        if self._today_production_kwh == value:
            return False

        self._today_production_kwh = value
        _LOGGER.debug("Today's Franklin production today updated: %.2f kWh", value)
        return True

class FranklinGridService(GridService):
    """Grid data service for FranklinWH gateway."""

    def __init__(self, hass: HomeAssistant) -> None:
        # Define handlers
        handlers: dict[str, VEEntityStateChangeHandler] = {
            "sensor.franklinwh_grid_export": self._handle_today_export_change,
            "sensor.franklinwh_grid_import": self._handle_today_import_change,
            "sensor.franklinwh_home_load": self._handle_now_home_load_change,
        }
        super().__init__(hass, handlers)

    def _handle_today_export_change(self, entity_id, old_state, new_state) -> bool:
        try:
            value = float(new_state.state)
        except ValueError:
            _LOGGER.warning("Failed to parse Franklin export today from state: %s", new_state.state)
            return False

        if self._today_export_kwh == value:
            return False

        self._today_export_kwh = value
        _LOGGER.debug("Franklin export today now updated: %.2f", value)
        return True

    def _handle_today_import_change(self, entity_id, old_state, new_state) -> bool:
        try:
            value = float(new_state.state)
        except ValueError:
            _LOGGER.warning("Failed to parse Franklin import today from state: %s", new_state.state)
            return False

        if self._today_import_kwh == value:
            return False

        self._today_import_kwh = value
        _LOGGER.debug("Franklin import today now updated: %.2f", value)
        return True

    def _handle_now_home_load_change(self, entity_id, old_state, new_state) -> bool:
        try:
            value = float(new_state.state)
        except ValueError:
            _LOGGER.warning("Failed to parse Franklin home load now from state: %s",
                            new_state.state)
            return False

        if self._today_import_kwh == value:
            return False

        self._today_import_kwh = value
        _LOGGER.debug("Franklin home load now updated: %.2f", value)
        return True

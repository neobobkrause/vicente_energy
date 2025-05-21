"""ChargePoint EV charger service implementation."""

import logging
from typing import Optional

from homeassistant.core import HomeAssistant, State

from .ev_charger_service import (
    EVChargerService,
    EVChargerState,
    convert_amps_to_kw,
    convert_kw_to_amps,
)
from .service import VEEntityStateChangeHandler

CHARGEPOINT_STATE_MAP = {
    "disconnected": EVChargerState.CHARGER_DISCONNECTED,
    "waiting for car demand": EVChargerState.CHARGER_WAITING,
    "charging": EVChargerState.CHARGER_CHARGING,
    "paused": EVChargerState.CHARGER_PAUSED,
    "finishing": EVChargerState.CHARGER_FINISHED,
    "locked": EVChargerState.CHARGER_LOCKED,
    "error": EVChargerState.CHARGER_ERROR,
    "waiting in queue by eco-smart": EVChargerState.CHARGER_QUEUED,
}

_LOGGER = logging.getLogger(__name__)

class ChargepointEVChargerService(EVChargerService):
    """Interact with a ChargePoint charger via Home Assistant sensors."""

    def __init__(self, hass: Optional[HomeAssistant]) -> None:
        """Set up entity handlers for ChargePoint sensors."""
        # Define handlers
        handlers: dict[str, VEEntityStateChangeHandler] = {
            "sensor.cph25_power_output": self._handle_power_change,
            "sensor.cph25_charging_status": self._handle_charger_state_change,
        }
        super().__init__(hass, handlers)
        self._max_charging_power_amps = 32

    async def set_charging_power_amps(self, power_amps: int) -> None:
        """Set charging current in amps via Home Assistant service."""
        _LOGGER.debug("Setting charging power to %.2f kW (%.1f A)", convert_amps_to_kw(power_amps, self._voltage), power_amps)

        try:
            await self._hass.services.async_call(
                "number",
                "set_value",
                {
                    "entity_id": f"number.wallbox_{self._location}_max_charging_current",
                    "value": round(power_amps)
                },
                blocking = True
            )
            _LOGGER.debug("Wallbox charging power changed: %.2f kW", power_amps)
        except ValueError:
            _LOGGER.debug("Unable to change Wallbox charging power value: %.2f kW", power_amps)

    async def set_charging_power_kw(self, power_kw: float) -> None:
        """Set charging power in kW via helper that converts to amps."""
        await self.set_charging_power_amps(convert_kw_to_amps(power_kw, self._voltage))


    def _handle_charger_state_change(self, entity_id: str, old_state: State, new_state: State) -> bool:
        """Handle updates to the charger state sensor."""
        try:
            mapped = CHARGEPOINT_STATE_MAP.get(new_state.state.lower(), EVChargerState.CHARGER_UNKNOWN)
        except ValueError:
            _LOGGER.debug("Unable to change Wallbox charging state: %s", new_state.state)
            return False

            if self._charger_state == mapped:
                return False

        self._charger_state = mapped
        _LOGGER.debug("Wallbox entity %s changed: %s → %s(%s)", entity_id, old_state.state.lower(), new_state.state.lower(), mapped)
        return True

    def _handle_power_change(self, entity_id: str, old_state: State, new_state: State) -> bool:
        """Handle updates to the charging power sensor."""
        try:
            value = convert_amps_to_kw(int(new_state.state), self._voltage)
        except ValueError:
            _LOGGER.debug("Ignoring bad charging power value: %s", new_state.state.lower())
            return False

        if self._charging_power_kw == value:
            return False

        self._charging_power_kw = value
        _LOGGER.debug("Charging power updated: %.2f kW", value)
        return True


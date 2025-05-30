"""Wallbox EV charger service implementation."""

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

WALLBOX_STATE_MAP = {
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

class WallboxEVChargerService(EVChargerService):
    """Interface with a Wallbox charger via HA entities."""

    def __init__(self, hass: Optional[HomeAssistant]) -> None:
        self._location: Optional[str] = None

        super().__init__(hass, {})
        self._max_charging_power_amps = 48

    async def connect(self):
        # Step 1: Find Wallbox sensor ending with _charging_power
        for state in self._hass.states.async_all():
            entity_id = state.entity_id
            if entity_id.startswith("sensor.wallbox_") and entity_id.endswith("_charging_power"):
                # entity_id = "sensor.wallbox_vicentecanyon1_charging_power"
                # strip domain and "sensor.wallbox_"
                entity_suffix = entity_id[len("sensor.wallbox_"):]
                # "vicentecanyon1_charging_power" → ["vicentecanyon1", "charging", "power"]
                parts = entity_suffix.split("_")
                self._location = "_".join(parts[:-2])  # strip off trailing 'charging_power'
                break

        if not self._location:
            raise RuntimeError("Wallbox location not found in entity namespace")

        # Step 2: Construct full entity IDs
        def full(name: str) -> str:
            return f"sensor.wallbox_{self._location}_{name}"

        # Step 3: Define handlers
        handlers: dict[str, VEEntityStateChangeHandler] = {
            full("charging_power"): self._handle_power_change,
            full("status_description"): self._handle_charger_state_change,
        }

        # Step 4: Set up tracking
        await self.set_handler_map(handlers)

    def get_location(self) -> Optional[str]:
        return self._location

    async def set_charging_power_amps(self, power_amps: int) -> None:
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
        await self.set_charging_power_amps(convert_kw_to_amps(power_kw, self._voltage))


    def _handle_charger_state_change(self, entity_id: str, old_state: State, new_state: State) -> bool:
        try:
            mapped = WALLBOX_STATE_MAP.get(new_state.state.lower(), EVChargerState.CHARGER_UNKNOWN)
        except ValueError:
            _LOGGER.debug("Unable to change Wallbox charging state: %s", new_state.state)
            return False

            if self._charger_state == mapped:
                return False

        self._charger_state = mapped
        _LOGGER.debug("Wallbox entity %s changed: %s → %s(%s)", entity_id, old_state.state.lower(), new_state.state.lower(), mapped)
        return True

    def _handle_power_change(self, entity_id: str, old_state: State, new_state: State) -> bool:
        try:
            value = float(new_state.state)
        except ValueError:
            _LOGGER.debug("Ignoring bad charging power value: %s", new_state.state.lower())
            return False

        if self._charging_power_kw == value:
            return False

        self._charging_power_kw = value
        _LOGGER.debug("Charging power updated: %.2f kW", value)
        return True


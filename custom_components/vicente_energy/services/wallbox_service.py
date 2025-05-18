import asyncio
import logging
from typing import Optional

from .ev_charger_service import EVChargerService

WALLBOX_STATE_MAP = {
    "disconnected": EVChargerState.CHARGER_DISCONNECTED,
    "waiting for car demand": EVChargerState.CHARGER_WAITING,
    "charging": EVChargerState.CHARGER_CHARGING,
    "paused": EVChargerState.CHARGER_PAUSED,
    "finishing": EVChargerState.CHARGER_FINISHING,
    "locked": EVChargerState.CHARGER_LOCKED,
    "error": EVChargerState.CHARGER_ERROR,
    "waiting in queue by eco-smart": EVChargerState.CHARGER_QUEUED,
}

_LOGGER = logging.getLogger(__name__)

class WallboxEVChargerService(EVChargerService):
    def __init__(self, hass):
        self._location: Optional[str] = None

        super().__init__(hass, None)

    async def connect(self):
        # Step 1: Find Wallbox sensor ending with _charging_power
        for state in self._hass.states.async_all():
            entity_id = state.entity_id
            if entity_id.startswith("sensor.wallbox_") and entity_id.endswith("_charging_power"):
                self._location = entity_id.split("_")[1]  # assumes one-word location
                break

        if not self._location:
            raise RuntimeError("Wallbox location not found in entity namespace")

        # Step 2: Construct full entity IDs
        def full(name: str) -> str:
            return f"sensor.wallbox_{self._location}_{name}"

        # Step 3: Define handlers
        handlers = {
            full("charging_power"): self._handle_power_change,
            full("status_description"): self._handle_state_change,
        }

        # Step 4: Set up tracking
        await self.set_handler_map(handlers)

    def get_location(self) -> str:
        return self._location

    async def set_charging_power_amps(self, power_amps: float) -> None:
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
                _LOGGER.debug("Wallbox charging power changed: %.2f kW", power_amps)
            )
        except ValueError:
            _LOGGER.debug("Unable to change Wallbox charging power value: %.2f kW", power_amps)

    async def set_charging_power_kw(self, power_kw: float) -> None:
        await self.set_charging_power_amps(convert_kw_to_amps(power_kw, self._voltage))


    def _handle_state_change(self, entity_id, old_state, new_state) -> bool:
        if new_state is None or old_state is None or new_state.state == old_state.state:
            return False  # No actual changeß

        mapped = WALLBOX_STATE_MAP.get(new_state.state.lower(), EVChargerState.UNKNOWN)
        _LOGGER.debug("Wallbox entity %s changed: %s → %s(%s)", entity_id, old_state.state.lower(), new_state.state.lower(), mapped)
        self._charger_state = mapped

        return True

    def _handle_power_change(self, entity_id, old_state, new_state) -> bool:
        if new_state is None or old_state is None or new_state.state == old_state.state:
            return False  # No actual change

        try:
            charging_power_kw = float(new_state.state)
            self._charging_power_kw = charging_power_kw
            _LOGGER.debug("Charging power updated: %.2f kW", self._charging_power_kw)
            return True
        except ValueError:
            _LOGGER.debug("Ignoring bad charging power value: %s", new_state.state.lower())
            return False


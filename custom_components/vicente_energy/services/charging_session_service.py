from datetime import timedelta
from typing import cast
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval
from ..services import ServiceType
from .service import VEService
from .ev_charger_service import EVChargerService, convert_kw_to_amps
from .budget_service import ChargingBudgetService

class ChargingSessionService(VEService):
    """EV Charging Session Manager Service for Vicente Energy Integration."""

    def __init__(self, hass: HomeAssistant):
        """Initialize the ChargingSessionService."""
        self._session_active = False
        self._update_interval = timedelta(minutes=1)
        super().__init__(hass, None)

    async def connect(self):
        """Setup the Charging Session Service."""
        service_manager = self._get_service_manager()
        entity_manager = self._get_entity_manager()
        await entity_manager.register_entity("charging_session_state",
                                             "sensor",
                                             None,
                                             "Charging Session State")
        await entity_manager.register_entity("charging_power_level_kw",
                                             "sensor",
                                             "kW",
                                             "Charging Power Level")
        await entity_manager.register_entity("charging_power_level_amps",
                                             "sensor",
                                             "amps",
                                             "Charging Power Level")
        async_track_time_interval(self._hass, self._periodic_update, self._update_interval)

    async def _periodic_update(self, now):
        """Perform charging decisions at regular intervals."""
        await self._evaluate_charging_conditions()

    async def _evaluate_charging_conditions(self):
        """Evaluate and manage the EV charging session based on current conditions."""
        service_manager = self._get_service_manager()
        budget_service: ChargingBudgetService = cast(ChargingBudgetService,
                                                     service_manager.get_service(
                                                         ServiceType.BUDGET_SERVICE))
        charger_service: EVChargerService = cast(EVChargerService,
                                                 service_manager.get_service(
                                                     ServiceType.EV_CHARGER_SERVICE))
        budget_kwh = budget_service.get_charging_budget_kwh()
        charge_power_kw = charger_service.get_charging_power_kw()
        max_charger_power_kw = charger_service.get_max_charging_power_kw()

        optimal_charge_rate_kw = min(budget_kwh, max_charger_power_kw)

        if optimal_charge_rate_kw <= 0:
            await self._stop_charging()
        else:
            await self._start_or_adjust_charging(optimal_charge_rate_kw)

    async def _start_or_adjust_charging(self, rate_kw):
        """Start or adjust the charging session to a specified power rate."""
        service_manager = self._get_service_manager()
        charger_service: EVChargerService = cast(EVChargerService,
                                                 service_manager.get_service(
                                                     ServiceType.EV_CHARGER_SERVICE))
        if not self._session_active or rate_kw != charger_service.get_charging_power_kw():
            await charger_service.set_charging_power_kw(rate_kw)
            self._session_active = True
            entity_manager = self._get_entity_manager()
            await entity_manager.update_entity("charging_session_state", "charging_active")
            await entity_manager.update_entity("charging_power_level_kw", rate_kw)
            await entity_manager.update_entity("charging_power_level_amps",
                                               convert_kw_to_amps(rate_kw))

    async def _stop_charging(self):
        """Stop the charging session if active."""
        if self._session_active:
            service_manager = self._get_service_manager()
            charger_service: EVChargerService = cast(EVChargerService,
                                                     service_manager.get_service(
                                                         ServiceType.EV_CHARGER_SERVICE))
            await charger_service.set_charging_power_kw(0)
            self._session_active = False
            entity_manager = self._get_entity_manager()
            await entity_manager.update_entity("charging_session_state", "idle")
            await entity_manager.update_entity("charging_power_level_kw", 0)
            await entity_manager.update_entity("charging_power_level_amps", 0)

    async def handle_ev_plugged_in(self):
        """Handle the EV plugged-in event."""
        await self._evaluate_charging_conditions()

    async def handle_ev_unplugged(self):
        """Handle the EV unplugged event."""
        await self._stop_charging()

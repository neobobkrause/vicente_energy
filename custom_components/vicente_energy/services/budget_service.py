"""EV charging energy budgeting service."""

from typing import List, cast
from homeassistant.core import HomeAssistant, State

from ..services import ServiceType
from .ev_charger_service import EVChargerService
from .grid_service import GridService
from .battery_service import BatteryService
from .forecast_service import ForecastService
from .solar_service import SolarService
from .service import VEService

CONF_BATTERY_RESERVE = "sensor.ve_battery_reserve"

class ChargingBudgetService(VEService):
    """EV charging energy budgeting service class"""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize default budget state."""
        self._charging_budget_kwh: float = 0.0

        """Register as interested in changes in other services"""
        self._show_interest([ServiceType.EV_CHARGER_SERVICE,
                             ServiceType.BATTERY_SERVICE,
                             ServiceType.SOLAR_SERVICE,
                             ServiceType.GRID_SERVICE,
                             ServiceType.FORECAST_SERVICE
                         ])

        super().__init__(hass, None)

    async def connect(self):
        """Setup the Charging Budget Service and register entities."""
        await self._get_entity_manager().register_entity(
            entity_id="charging_budget_kwh",
            entity_type="sensor",
            unit="kWh",
            description="Available Charging Budget (kWh)"
        )

    def get_charging_budget_kwh(self) -> float:
        """Return the amount of power available for EV charging in kWh."""
        return self._charging_budget_kwh

    def _show_interest(self, interests: List[ServiceType]) -> None:
        """Register as interested in changes in other services"""
        service_manager = self._get_service_manager()
        for service_type in interests:
            service = service_manager.get_service(service_type)
            if service is None:
                raise ValueError(f"No service found for service type '{service_type}'")
            service.register_callback(self._handle_something_changing)

    def _handle_something_changing(self,
                                   _entity_id: str,
                                   _old_state: State,
                                   _new_state: State) -> bool:
        """Calculate and update the available kWh charging budget based on system states."""
        service_manager = self._get_service_manager()
        entity_manager = self._get_entity_manager()

        # Obtain references to other services
        solar_service: SolarService = cast(SolarService,
                                           service_manager.get_service(
                                               ServiceType.SOLAR_SERVICE))
        battery_service: BatteryService = cast(BatteryService,
                                               service_manager.get_service(
                                                   ServiceType.BATTERY_SERVICE))
        grid_service: GridService = cast(GridService,
                                         service_manager.get_service(
                                             ServiceType.GRID_SERVICE))
        forecast_service: ForecastService = cast(ForecastService,
                                                 service_manager.get_service(
                                                     ServiceType.FORECAST_SERVICE))
        charger_service: EVChargerService = cast(EVChargerService,
                                                 service_manager.get_service(
                                                     ServiceType.EV_CHARGER_SERVICE))

        # Get current energy states
        current_solar_kw = solar_service.get_current_production_kw()
        current_battery_soc = battery_service.get_battery_soc()
        battery_capacity_kwh = battery_service.get_storage_capacity_kwh()
        min_battery_soc_pct = battery_service.get_battery_reserve_pct()

        # Forecasted solar production for the next hour
        next_hour_solar_kwh = forecast_service.get_next_hour_production_kwh()

        # Current grid import/export state
        grid_import_kwh = grid_service.get_today_import_kwh()
        grid_export_kwh = grid_service.get_today_export_kwh()

        # Current household load
        current_house_load_kw = grid_service.get_current_home_load_kw()

        # Charger capability (maximum supported rate)
        charger_max_power_kw = charger_service.get_max_charging_power_kw()

        # Calculate surplus solar available (current surplus plus next hour forecast)
        excess_production = current_solar_kw - current_house_load_kw
        available_solar_kwh = max(excess_production, 0)\
            + forecast_service.get_this_hour_production_kwh()\
            + forecast_service.get_next_hour_production_kwh()

        # Calculate battery energy available for discharge (beyond minimum reserve)
        available_battery_kwh = max(
            ((current_battery_soc - min_battery_soc_pct) / 100.0) * battery_capacity_kwh, 0
        )

        # Grid energy availability within allowed limits
        available_grid_kwh = 0

        # Aggregate total available energy for charging
        total_available_kwh = available_solar_kwh + available_battery_kwh + available_grid_kwh

        # Limit budget by the charger's maximum supported rate
        optimal_budget_kwh = min(total_available_kwh, charger_max_power_kw)

        # Update internal budget state
        self._charging_budget_kwh = optimal_budget_kwh

        # Publish the budget entity update
        self._hass.loop.create_task(
            entity_manager.update_entity("charging_budget_kwh", optimal_budget_kwh))

        return True

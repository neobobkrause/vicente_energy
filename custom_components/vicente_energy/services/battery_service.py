"""Abstract battery storage service."""

from typing import Optional
from homeassistant.core import HomeAssistant

from .service import VEEntityStateChangeHandler, VEService


class BatteryService(VEService):
    """Base class for battery system integrations."""

    def __init__(self, hass: HomeAssistant,
                 entity_handlers: Optional[dict[str, VEEntityStateChangeHandler]] = None) -> None:
        """Initialize default battery state."""
        self._storage_capacity_kwh: float = 0.0
        self._battery_soc: float = 0.0  # 0–100
        self._storage_power_kw: float = 0.0
        self._today_charge_kwh: float = 0.0
        self._today_discharge_kwh: float = 0.0

        super().__init__(hass, entity_handlers)

    async def get_battery_soc(self) -> float:
        """Return current battery state of charge percentage."""
        return self._battery_soc

    async def get_storage_energy_kwh(self) -> float:
        """Return stored energy based on capacity and SOC."""
        return self._storage_capacity_kwh * (self._battery_soc / 100.0)

    async def get_today_charge_kwh(self) -> float:
        """Return energy charged today in kWh."""
        return self._today_charge_kwh

    async def get_today_discharge_kwh(self) -> float:
        """Return energy discharged today in kWh."""
        return self._today_discharge_kwh

    async def get_storage_capacity_kwh(self) -> float:
        """Return configured storage capacity in kWh."""
        return self._storage_capacity_kwh

    async def set_storage_capacity_kwh(self, capacity_kwh: float) -> None:
        """Update the battery capacity setting."""
        self._storage_capacity_kwh = capacity_kwh

    async def get_storage_power_kw(self) -> float:
        """Return current battery charging/discharging power."""
        return self._storage_power_kw

    async def set_storage_power_kw(self, power_kw: float) -> None:
        """Set the instantaneous power flow for the battery."""
        self._storage_power_kw = power_kw

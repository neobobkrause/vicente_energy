from homeassistant.core import HomeAssistant
from .service import VEService, VEEntityStateChangeHandler

class BatteryService(VEService):
    def __init__(self, hass: HomeAssistant, entity_handlers: dict[str, VEEntityStateChangeHandler]) -> None:
        self._storage_capacity_kwh: float = 0.0
        self._battery_soc: float = 0.0  # 0–100
        self._storage_power_kw: float = 0.0
        self._today_charge_kwh: float = 0.0
        self._today_discharge_kwh: float = 0.0

        super().__init__(hass, entity_handlers)

    async def get_battery_soc(self) -> float:
        return self._battery_soc

    async def get_storage_energy_kwh(self) -> float:
        return self._storage_capacity_kwh * (self._battery_soc / 100.0)

    async def get_today_charge_kwh(self) -> float:
        return self._today_charge_kwh

    async def get_today_discharge_kwh(self) -> float:
        return self._today_discharge_kwh

    async def get_storage_capacity_kwh(self) -> float:
        return self._storage_capacity_kwh

    async def set_storage_capacity_kwh(self, capacity_kwh: float) -> None:
        self._storage_capacity_kwh = capacity_kwh

    async def get_storage_power_kw(self) -> float:
        return self._storage_power_kw

    async def set_storage_power_kw(self, power_kw: float) -> None:
        self._storage_power_kw = power_kw

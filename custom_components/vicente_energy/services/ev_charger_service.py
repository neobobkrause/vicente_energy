from enum import StrEnum


class EVChargerState(StrEnum):
    CHARGER_UNKNOWN = "unknown"
    CHARGER_DISCONNECTED = "disconnected"
    CHARGER_WAITING = "waiting"
    CHARGER_CHARGING = "charging"
    CHARGER_PAUSED = "paused"
    CHARGER_FINISHED = "finished"
    CHARGER_LOCKED = "locked"
    CHARGER_ERROR = "error"
    CHARGER_QUEUED = "queued"

DEFAULT_CHARGER_VOLTAGE = 240  # residential split-phase typical

def convert_kw_to_amps(power_kw: float, voltage: float = DEFAULT_CHARGER_VOLTAGE) -> float:
    return (power_kw * 1000) / voltage

def convert_amps_to_kw(power_a: float, voltage: float = DEFAULT_CHARGER_VOLTAGE) -> float:
    return (power_kw * 1000) / voltage

class EVChargerService(VEService):
    def __init__(self, hass, entity_handlers: dict[str, VEEntityStateChangeHandler]):
        self._charger_state = EVChargerState.CHARGER_UNKNOWN
        self._voltage = DEFAULT_CHARGER_VOLTAGE
        self._max_charging_power_amps = 0
        self._charging_power_kw = 0

        super().__init__(hass, entity_handlers)

    async def get_charger_state(self) -> EVChargerState:
        return self._charger_state

    async def get_charging_power_amps(self) -> float:
        return convert_kw_to_amps(self._charging_power_kw, self._voltage)

    async def get_charging_power_kw(self) -> float:
        return self._charging_power_kw

    async def get_max_charging_power_kw(self) -> float:
        return convert_amps_to_kw(self._max_charging_power_amps, self._voltage)

    async def get_max_charging_power_amps(self) -> float:
        return self._max_charging_power_amps

    async def get_charger_voltage(self) -> int:
        return self._voltage

    async def set_charger_voltage(self, voltage: int) -> None:
        self._voltage = voltage

    @abstractmethod
    async def set_charging_power_amps(self, power_amps: float) -> None:
        pass

    @abstractmethod
    async def set_charging_power_kw(self, power_kw: float) -> None:
        pass

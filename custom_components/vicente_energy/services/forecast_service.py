from .service import VEEntityStateChangeHandler, VEService


class ForecastService(VEService):
    def __init__(self, hass, entity_handlers: dict[str, VEEntityStateChangeHandler]):
        self._today_production_kwh: float = 0.0
        self._tomorrow_production_kwh: float = 0.0
        self._now_production_kw: float = 0.0

        super().__init__(hass, entity_handlers)

    async def get_today_production_kwh(self) -> float:
        return _today_production_kwh

    async def get_tomorrow_production_kwh(self) -> float:
        return _tomorrow_production_kwh

    async def get_now_production_kw(self) -> float:
        return _now_production_kw

    async def get_this_hour_production_kwh(self) -> float:
        current_hour = datetime.now().hour  # 0 through 23
        return self._get_today_hour_production_kwh(current_hour)

    async def get_next_hour_production_kwh(self) -> float:
        current_hour = datetime.now().hour  # 0 through 23
        if (current_hour == 23):
            return self._get_tomorrow_hour_production_kwh(0)

        return self._get_today_hour_production_kwh(current_hour+1)

    @abstractmethod
    async def _get_today_hour_production_kwh(self, hour: int) -> float:
        pass

    @abstractmethod
    async def _get_tomorrow_hour_production_kwh(self, hour: int) -> float:
        pass


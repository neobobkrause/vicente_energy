from .service import VEService, VEEntityStateChangeHandler

class SolarService(VEService):
    def __init__(self, hass, entity_handlers: dict[str, VEEntityStateChangeHandler]):
        self._now_production_kw: float = 0.0
        self._today_production_kwh: float = 0.0

        super().__init__(hass, entity_handlers)

    async def get_now_production_kw(self) -> float:
        return self._now_production_kw

    async def get_today_production_kwh(self) -> float:
        return self._today_production_kwh


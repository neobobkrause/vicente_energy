"""Base class for grid energy service providers."""

from .service import VEEntityStateChangeHandler, VEService


class GridService(VEService):
    """Represent grid import/export measurements."""

    def __init__(self, hass, entity_handlers: dict[str, VEEntityStateChangeHandler]):
        """Initialize default state values."""
        self._today_export_kwh: float = 0.0
        self._today_import_kwh: float = 0.0
        self._now_home_load_kw: float = 0.0

        super().__init__(hass, entity_handlers)

    async def get_today_export_kwh(self) -> float:
        return self._today_export_kwh

    async def get_today_import_kwh(self) -> float:
        return self._today_import_kwh

    async def get_now_home_load_kw(self) -> float:
        return self._now_home_load_kw


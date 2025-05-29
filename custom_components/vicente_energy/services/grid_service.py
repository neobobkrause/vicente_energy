"""Base class for grid energy service providers."""

from typing import Optional
from .service import VEEntityStateChangeHandler, VEService


class GridService(VEService):
    """Represent grid import/export measurements."""

    def __init__(self, hass,
                 entity_handlers: Optional[dict[str, VEEntityStateChangeHandler]] = None):
        """Initialize default state values."""
        self._today_export_kwh: float = 0.0
        self._today_import_kwh: float = 0.0
        self._current_home_load_kw: float = 0.0

        super().__init__(hass, entity_handlers)

    def get_today_export_kwh(self) -> float:
        return self._today_export_kwh

    def get_today_import_kwh(self) -> float:
        return self._today_import_kwh

    def get_current_home_load_kw(self) -> float:
        return self._current_home_load_kw

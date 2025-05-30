"""Gather raw sensor signals for Vicente Energy calculations."""

from homeassistant.core import HomeAssistant

from .models import Signals
from .services.service_manager import ServiceManager


class InputCollector:
    """Collect sensor inputs and optional external service data."""

    def __init__(self, hass: HomeAssistant, *args,
                 solar_power_entity: str = None,
                 solar_forecast_entities: list = None,
                 battery_soc_entity: str = None,
                 house_load_entity: str = None,
                 wallbox_power_entity: str = None,
                 inverter_on_entity: str = None,
                 wallbox_state_entity: str = None,
                 # legacy names
                 solar_entity: str = None,
                 battery_entity: str = None,
                 load_entity: str = None,
                 service_manager: ServiceManager = None):
        """Initialize with entity IDs and optional service manager.

        Legacy positional arguments are supported for backwards compatibility.
        """
        # Legacy positional args mapping:
        if len(args) >= 5:
            # Map first 5 positional args to entity IDs
            solar_power_entity   = solar_power_entity   or args[0]
            battery_soc_entity   = battery_soc_entity   or args[1]
            house_load_entity    = house_load_entity    or args[2]
            wallbox_power_entity = wallbox_power_entity or args[3]
            inverter_on_entity   = inverter_on_entity   or args[4]
        if len(args) >= 6:
            wallbox_state_entity = wallbox_state_entity or args[5]

        # Map old names → new names
        solar_power_entity = solar_power_entity or solar_entity
        battery_soc_entity = battery_soc_entity or battery_entity
        house_load_entity  = house_load_entity  or load_entity

        self.hass = hass
        self._solar_power_entity      = solar_power_entity
        self._solar_forecast_entities = solar_forecast_entities or []
        self._battery_soc_entity      = battery_soc_entity
        self._house_load_entity       = house_load_entity
        self._wallbox_power_entity    = wallbox_power_entity
        self._inverter_on_entity      = inverter_on_entity
        self._wallbox_state_entity    = wallbox_state_entity
        # Store the ServiceManager (if any) for external data (e.g., Wallbox API)
        self.service_manager = service_manager

    def get_signals(self) -> Signals:
        """Return current Signals dataclass populated from sensors."""
        # Solar power
        sp = self.hass.states.get(self._solar_power_entity) if self._solar_power_entity else None
        solar_power = float(sp.state) if sp and hasattr(sp, "state") else 0.0
        # Battery SOC
        bs = self.hass.states.get(self._battery_soc_entity)
        battery_soc = float(bs.state) if bs and hasattr(bs, "state") else 0.0
        # House load
        hl = self.hass.states.get(self._house_load_entity)
        house_load = float(hl.state) if hl and hasattr(hl, "state") else 0.0

        # EV charger power measurement
        wallbox_power = 0.0
        if self.service_manager and hasattr(self.service_manager, "get_charger_state"):
            # Use external Wallbox service data if available
            charger_state = self.service_manager.get_charger_state()
            if isinstance(charger_state, dict) and 'charging_power' in charger_state:
                try:
                    wallbox_power = float(charger_state['charging_power'])
                except (ValueError, TypeError):
                    wallbox_power = 0.0
        elif self._wallbox_power_entity:
            # Fallback to local sensor
            wp_state = self.hass.states.get(self._wallbox_power_entity)
            if wp_state and hasattr(wp_state, "state"):
                try:
                    wallbox_power = float(wp_state.state)
                except ValueError:
                    wallbox_power = 0.0

        # Inverter on/off
        inv = self.hass.states.get(self._inverter_on_entity)
        inv_on = False
        if inv and hasattr(inv, "state"):
            inv_on = str(inv.state).lower() in ("on", "true", "1")
        return Signals(
            solar_power_w=solar_power,
            battery_soc_pct=battery_soc,
            house_load_total_w=house_load,
            wallbox_power_w=wallbox_power,
            agate_inverter_on=inv_on
        )

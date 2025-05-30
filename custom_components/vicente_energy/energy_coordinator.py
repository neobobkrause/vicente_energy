"""Utility helpers for aggregating energy statistics."""


class EnergyCoordinator:
    """Coordinate data between battery and solar services."""

    def __init__(self, battery_service, solar_service, hass):
        """Store service references and Home Assistant handle."""
        self.battery_service = battery_service
        self.solar_service = solar_service
        self.hass = hass

    def get_home_load_today(self):
        """Return today's calculated home load."""
        battery_charge_today = self.battery_service.get_battery_charge_today()
        battery_discharge_today = self.battery_service.get_battery_discharge_today()
        grid_import_today = self.battery_service.get_grid_import_today()
        grid_export_today = self.battery_service.get_grid_export_today()
        solar_production_today = self.solar_service.get_total_energy_today()

        home_load_today = (
            solar_production_today
            + grid_import_today
            + battery_discharge_today
            - grid_export_today
            - battery_charge_today
        )

        return home_load_today

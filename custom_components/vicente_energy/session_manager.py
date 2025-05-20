from datetime import datetime, timedelta


class SessionManager:
    def __init__(self, hass, state_manager):
        self.hass = hass
        self.state = state_manager
        self.session_start_time = None
        self.session_kwh_used = 0.0
        self.session_duration = timedelta()
        self.session_available_after = 0.0
        self.charge_state = "unplugged"
        self.active = False
        self.budget_remaining = 0.0
        self.estimates = None

    def is_active(self):
        return self.charge_state == "active_session"

    def update_charge_state(self, wallbox_state):
        old_state = self.charge_state
        if wallbox_state == "charging":
            if old_state != "active_session":
                self.charge_state = "active_session"
                self.session_start_time = datetime.now()
                self.session_kwh_used = 0.0
                self.active = True
        elif wallbox_state == "plugged":
            self.charge_state = "plugged_no_session"
            self.active = False
        elif wallbox_state == "done":
            if old_state == "active_session":
                self.finalize_session()
            self.charge_state = "plugged_post_session"
            self.active = False
        elif wallbox_state == "unplugged":
            if old_state == "active_session":
                self.finalize_session()
            self.charge_state = "unplugged"
            self.active = False

    def set_power_level(self, power_kw):
        self.current_power_kw = power_kw

    def set_estimates(self, estimates):
        self.estimates = estimates
        self.session_available_after = estimates.available_after_kwh

    def set_budget(self, budget_kwh):
        self.budget_remaining = budget_kwh

    def increment_energy(self, elapsed_minutes):
        if self.active and hasattr(self, "current_power_kw"):
            added_kwh = self.current_power_kw * (elapsed_minutes / 60)
            self.session_kwh_used += added_kwh
            self.budget_remaining -= added_kwh
            self.session_duration = datetime.now() - self.session_start_time

    def finalize_session(self):
        """Finalize the current session, updating learned bias and storing last session usage."""
        if self.session_start_time:
            self.session_duration = datetime.now() - self.session_start_time
        # Update session bias using actual vs estimated session kWh
        self.state.learn_session_bias(actual_kwh=self.session_kwh_used,
                                      estimated_kwh=(self.estimates.kwh_estimated if self.estimates else 0.0))
        # Record the total session kWh
        self.state.save_last_session_kwh(self.session_kwh_used)


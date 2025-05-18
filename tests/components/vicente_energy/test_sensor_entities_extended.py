from datetime import datetime, timedelta

from custom_components.vicente_energy.sensor import (
    AvailableAfterSensor,
    Budget24hSensor,
    ChargeStateSensor,
    SessionDurationSensor,
    SessionEnergyUsedSensor,
    SessionStartTimeSensor,
)
import pytest


class FakeCoordinator:
    def __init__(self, name, data):
        self.name = name
        self.data = data


class FakeSessionManager:
    def __init__(self):
        self.session_start_time = None
        self.session_duration = None
        self.session_kwh_used = None
        self.session_available_after = None
        self.charge_state = None


def test_unique_id_and_rounding():
    coord = FakeCoordinator("test", {"budget_24h_kwh": 1.234567})
    sensor = Budget24hSensor(coord)
    assert sensor.unique_id == "test_budget_24h_kwh"
    assert sensor.state == 1.235


def test_session_time_states():
    sm = FakeSessionManager()
    sm.session_start_time = datetime(2025, 1, 1, 0, 0, 0)
    sm.session_duration = timedelta(minutes=123)
    sm.session_kwh_used = 7.891
    sm.session_available_after = 4.321
    sm.charge_state = "plugged_no_session"

    s1 = SessionStartTimeSensor(sm)
    assert s1.state == "2025-01-01T00:00:00"
    s2 = SessionDurationSensor(sm)
    assert s2.state == 123
    s3 = SessionEnergyUsedSensor(sm)
    assert s3.state == pytest.approx(7.891, rel=1e-3)
    s4 = AvailableAfterSensor(sm)
    assert s4.state == pytest.approx(4.321, rel=1e-3)
    s5 = ChargeStateSensor(sm)
    assert s5.state == "plugged_no_session"

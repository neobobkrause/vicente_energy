from datetime import datetime, timedelta

from custom_components.vicente_energy.sensor import (
    AvailableAfterSensor,
    Budget24hSensor,
    ChargeStateSensor,
    PowerLevelSensor,
    SessionDurationSensor,
    SessionEnergyUsedSensor,
    SessionStartTimeSensor,
)


class FakeCoordinator:
    def __init__(self, data):
        self.data = data


class FakeSessionManager:
    def __init__(self):
        self.session_start_time = datetime(2025, 1, 1, 12, 0, 0)
        self.session_duration = timedelta(minutes=90)
        self.session_kwh_used = 5.6789
        self.session_available_after = 10.1234
        self.charge_state = "active_session"


def test_budget_sensor():
    sensor = Budget24hSensor(FakeCoordinator({"budget_24h_kwh": 12.3456}))
    assert sensor.state == 12.346


def test_power_level_sensor():
    sensor = PowerLevelSensor(FakeCoordinator({"power_level_kw": 3.14159}))
    assert sensor.state == 3.142


def test_session_start_time_sensor():
    sensor = SessionStartTimeSensor(FakeSessionManager())
    assert sensor.state == "2025-01-01T12:00:00"


def test_session_duration_sensor():
    sensor = SessionDurationSensor(FakeSessionManager())
    assert sensor.state == 90


def test_session_energy_used_sensor():
    sensor = SessionEnergyUsedSensor(FakeSessionManager())
    assert sensor.state == 5.679


def test_available_after_sensor():
    sensor = AvailableAfterSensor(FakeSessionManager())
    assert sensor.state == 10.123


def test_charge_state_sensor():
    sensor = ChargeStateSensor(FakeSessionManager())
    assert sensor.state == "active_session"

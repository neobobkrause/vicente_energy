# how many past signal samples we keep around for smoothing & bias calculations
SIGNAL_HISTORY_LENGTH = 24  

DOMAIN = "vicente_energy"

CONF_SOLAR_POWER_ENTITY = "solar_power_entity"
CONF_SOLAR_FORECAST_ENTITIES = "solar_forecast_entities"
CONF_BATTERY_SOC_ENTITY = "battery_soc_entity"
CONF_HOUSE_LOAD_ENTITY = "house_load_entity"
CONF_WALLBOX_POWER_ENTITY = "wallbox_power_entity"
CONF_INVERTER_ON_ENTITY = "inverter_on_entity"
CONF_WALLBOX_STATE_ENTITY = "wallbox_state_entity"

CONF_BATTERY_CAPACITY_KWH = "battery_capacity_kwh"
CONF_RESERVE_SOC_PCT = "reserve_soc_pct"
CONF_STORAGE_EFFICIENCY = "storage_efficiency"
CONF_MAX_CHARGER_POWER_KW = "max_charger_power_kw"
CONF_SESSION_LEARNING_ALPHA = "session_learning_alpha"
CONF_BUDGET_UPDATE_INTERVAL_HOURS = "budget_update_interval_hours"
CONF_UPDATE_INTERVAL_MINUTES = "update_interval_minutes"

DATA_HOURLY_COORDINATOR = "hourly_coordinator"
DATA_MINUTE_COORDINATOR = "minute_coordinator"
DATA_STATE_MANAGER = "state_manager"
DATA_LOAD_FORECASTER = "load_forecaster"
DATA_FORECAST_TRACKER = "forecast_accuracy_tracker"
DATA_CHARGE_ESTIMATOR = "charge_estimator"

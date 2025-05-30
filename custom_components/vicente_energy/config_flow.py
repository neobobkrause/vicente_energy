"""Configuration and options flow handlers for Vicente Energy."""

import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector
from homeassistant.data_entry_flow import FlowResult
from homeassistant.loader import async_get_integrations

from .const import (
    CONF_SOLAR_POWER_ENTITY,
    CONF_BATTERY_SOC_ENTITY,
    CONF_HOUSE_LOAD_ENTITY,
    CONF_EVCHARGER_POWER_ENTITY,
    CONF_EVCHARGER_STATE_ENTITY,
    CONF_LOCATION_NAME,
    CONF_SOLAR_FORECAST,
    CONF_EV_CHARGER,
    DOMAIN,
)

from .service_registry import SERVICE_CLASS_MAP
from .service_type import ServiceType

# Define available integration options (currently only one each, can expand in future)
AVAILABLE_EV_CHARGERS = ["Wallbox"]
AVAILABLE_SOLAR_FORECASTS = ["Solcast"]
MAX_NAME_LENGTH = 32

_LOGGER = logging.getLogger(__name__)

class VicenteEnergyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for the Vicente Energy integration."""
    VERSION = 1

    @staticmethod
    @config_entries.callback
    def async_get_options_flow(config_entry):
        """Return the OptionsFlow handler for this config entry."""
        return VicenteEnergyOptionsFlow(config_entry)

    async def async_step_import(self, import_config):
        """Handle import from YAML."""
        return await self.async_step_user(user_input=import_config)

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step of the config flow."""
        if user_input is not None:
            # Map friendly names back to internal domain names
            reverse_name_map = self.hass.data["vicente_energy_reverse_map"]
            translated_input = {
                key: reverse_name_map.get(value, value)
                for key, value in user_input.items()
            }

            return self.async_create_entry(
                title="Vicente Energy",
                data=translated_input
            )

        # Step 1: Get loaded integrations
        loaded_integrations = await async_get_loaded_integrations(self.hass)

        errors = {}

        # Step 2: Build schema dynamically based on what's available
        schema_fields = {
            vol.Required(CONF_LOCATION_NAME): str,
            vol.Required(CONF_BATTERY_CAPACITY_KWH): float,
            vol.Required(CONF_RESERVE_SOC_PCT, default=20): vol.All(
                vol.Coerce(int),
                vol.Range(min=0, max=100)
            ),
            vol.Required(CONF_STORAGE_EFFICIENCY, default=90): vol.All(
                vol.Coerce(float),
                vol.Range(min=10, max=100)
            )
        }

        reverse_name_map = {}  # friendly_name → domain
        for service_type in ServiceType:
            impls = SERVICE_CLASS_MAP.get(service_type, {})
            options = []

            for impl_name, cls in impls.items():
                domain = getattr(cls, "domain", None)
                if domain and domain in loaded_integrations:
                    # Try to use friendly name if available
                    friendly_name = loaded_integrations[domain].name
                    options.append(friendly_name)
                    reverse_name_map[friendly_name] = impl_name  # store for reverse lookup

            if options:
                schema_fields[
                    vol.Required(service_type.value, default=options[0])
                ] = vol.In(sorted(options))

        # Step 3: Cache reverse lookup map for when user submits
        self.hass.data["vicente_energy_reverse_map"] = reverse_name_map

        schema = vol.Schema(schema_fields)

        if user_input is not None:
            location_name = user_input[CONF_LOCATION_NAME].strip()

            # Preserve original check: Ensure location name isn't empty
            if not location_name:
                errors[CONF_LOCATION_NAME] = "name_empty"
            # Preserve original check: Ensure location name isn't too long
            elif len(location_name) > MAX_NAME_LENGTH:
                errors[CONF_LOCATION_NAME] = "name_too_long"

            # Preserve original suggested validation for duplicate entries
            existing_entries = self._async_current_entries()
            if any(entry.data.get(CONF_LOCATION_NAME) == location_name for entry in existing_entries):
                errors[CONF_LOCATION_NAME] = "already_configured"

            # All validations passed, create entry
            if not errors:
                return self.async_create_entry(
                    title=f"Vicente Energy ({location_name})",
                    data=user_input
                )

        # Display form again with any accumulated errors
        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors
        )

class VicenteEnergyOptionsFlow(config_entries.OptionsFlow):
    """Handle an options flow to allow configuration changes for Vicente Energy."""
    def __init__(self, config_entry):
        """Initialize the OptionsFlow with the current config entry."""
        self.config_entry = config_entry
        self.reverse_name_map = {}

    async def async_step_init(self, user_input=None):
        """Handle the first step of the options flow."""
        if user_input is not None:
            # Only remap fields corresponding to service types
            service_keys = {stype.value for stype in ServiceType}

            translated_input = {
                key: self.reverse_name_map.get(value, value) if key in service_keys else value
                for key, value in user_input.items()
            }

            return self.async_create_entry(data=translated_input)

        loaded_integrations = await async_get_loaded_integrations(self.hass)
        loaded_domains = set(loaded_integrations.keys())

        schema_fields = {}
        self.reverse_name_map = {}

        for service_type in ServiceType:
            impls = SERVICE_CLASS_MAP.get(service_type, {})
            options = []

            for impl_key, cls in impls.items():
                domain = getattr(cls, "domain", None)
                if domain and domain in loaded_domains:
                    friendly = loaded_integrations[domain].name
                    options.append(friendly)
                    self.reverse_name_map[friendly] = impl_key

            if options:
                current_impl = self.config_entry.options.get(service_type.value)
                current_cls = impls.get(current_impl)
                current_domain = getattr(current_cls, "domain", None)
                default_friendly = (
                    loaded_integrations[current_domain].name
                    if current_domain in loaded_integrations
                    else sorted(options)[0]
                )

                schema_fields[vol.Required(service_type.value, default=default_friendly)] = vol.In(sorted(options))

        # Add additional optional configuration fields
        schema_fields[vol.Required(
            CONF_LOCATION_NAME,
            default=self.config_entry.options.get(CONF_LOCATION_NAME, "")
        )] = vol.All(str, vol.Length(max=32))

        schema_fields[vol.Required(
            CONF_BATTERY_CAPACITY_KWH,
            default=self.config_entry.options.get(CONF_BATTERY_CAPACITY_KWH, 15)
        )] = vol.All(float, vol.Range(min=0.1))

        schema_fields[vol.Required(
            CONF_RESERVE_SOC_PCT,
            default=self.config_entry.options.get(CONF_RESERVE_SOC_PCT, 20)
        )] = vol.All(int, vol.Range(min=0, max=100))

        schema_fields[vol.Required(
            CONF_STORAGE_EFFICIENCY,
            default=self.config_entry.options.get(CONF_STORAGE_EFFICIENCY, 0.90)
        )] = vol.All(float, vol.Range(min=0.0, max=1.0))

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(schema_fields)
        )

def get_available_implementations(service_type: ServiceType, loaded_integrations: set[str]) -> list[str]:
    """Return list of implementation names for a given service_type where the integration is loaded."""
    implementations = SERVICE_CLASS_MAP.get(service_type, {})
    return [
        impl_name
        for impl_name, cls in get_configured_integrations(self.hass).items()
        if getattr(cls, "domain", None) in loaded_integrations
    ]

async def async_get_loaded_integrations(hass) -> set[str]:
    """Return a set of all loaded integration domains and log them."""
    loaded_integrations = await async_get_integrations(hass)

    _LOGGER.info("Loaded integrations found:")
    for domain, integration in loaded_integrations.items():
        _LOGGER.info(" - %s (name: %s)", domain, integration.name)

    return set(loaded_integrations.keys())

def get_configured_integrations(hass) -> set[str]:
    """Return a set of domains with at least one ConfigEntry."""
    domains = set()
    for entry in hass.config_entries.async_entries():
        domains.add(entry.domain)
    return domains


from homeassistant.helpers import selector
from homeassistant.data_entry_flow import FlowResult
from homeassistant.loader import async_get_integrations

from .const import (
    CONF_SOLAR_POWER_ENTITY,
    CONF_BATTERY_SOC_ENTITY,
    CONF_HOUSE_LOAD_ENTITY,
    CONF_EVCHARGER_POWER_ENTITY,
    CONF_EVCHARGER_STATE_ENTITY,
    CONF_LOCATION_NAME,
    CONF_SOLAR_FORECAST,
    CONF_EV_CHARGER,
    DOMAIN,
)

from .service_registry import SERVICE_CLASS_MAP
from .service_type import ServiceType

# Define available integration options (currently only one each, can expand in future)
AVAILABLE_EV_CHARGERS = ["Wallbox"]
AVAILABLE_SOLAR_FORECASTS = ["Solcast"]
MAX_NAME_LENGTH = 32

_LOGGER = logging.getLogger(__name__)

class VicenteEnergyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for the Vicente Energy integration."""
    VERSION = 1

    @staticmethod
    @config_entries.callback
    def async_get_options_flow(config_entry):
        """Return the OptionsFlow handler for this config entry."""
        return VicenteEnergyOptionsFlow(config_entry)

    async def async_step_import(self, import_config):
        """Handle import from YAML."""
        return await self.async_step_user(user_input=import_config)

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Process user step in duplicated flow block."""
        if user_input is not None:
            # Map friendly names back to internal domain names
            reverse_name_map = self.hass.data["vicente_energy_reverse_map"]
            translated_input = {
                key: reverse_name_map.get(value, value)
                for key, value in user_input.items()
            }

            return self.async_create_entry(
                title="Vicente Energy",
                data=translated_input
            )

        # Step 1: Get loaded integrations
        loaded_integrations = await async_get_loaded_integrations(self.hass)

        errors = {}

        # Step 2: Build schema dynamically based on what's available
        schema_fields = {
            vol.Required(CONF_LOCATION_NAME): str,
            vol.Required(CONF_BATTERY_CAPACITY_KWH): float,
            vol.Required(CONF_RESERVE_SOC_PCT, default=20): vol.All(
                vol.Coerce(int),
                vol.Range(min=0, max=100)
            ),
            vol.Required(CONF_STORAGE_EFFICIENCY, default=90): vol.All(
                vol.Coerce(float),
                vol.Range(min=10, max=100)
            )
        }

        reverse_name_map = {}  # friendly_name → domain
        for service_type in ServiceType:
            impls = SERVICE_CLASS_MAP.get(service_type, {})
            options = []

            for impl_name, cls in impls.items():
                domain = getattr(cls, "domain", None)
                if domain and domain in loaded_integrations:
                    # Try to use friendly name if available
                    friendly_name = loaded_integrations[domain].name
                    options.append(friendly_name)
                    reverse_name_map[friendly_name] = impl_name  # store for reverse lookup

            if options:
                schema_fields[
                    vol.Required(service_type.value, default=options[0])
                ] = vol.In(sorted(options))

        # Step 3: Cache reverse lookup map for when user submits
        self.hass.data["vicente_energy_reverse_map"] = reverse_name_map

        schema = vol.Schema(schema_fields)

        if user_input is not None:
            location_name = user_input[CONF_LOCATION_NAME].strip()

            # Preserve original check: Ensure location name isn't empty
            if not location_name:
                errors[CONF_LOCATION_NAME] = "name_empty"
            # Preserve original check: Ensure location name isn't too long
            elif len(location_name) > MAX_NAME_LENGTH:
                errors[CONF_LOCATION_NAME] = "name_too_long"

            # Preserve original suggested validation for duplicate entries
            existing_entries = self._async_current_entries()
            if any(entry.data.get(CONF_LOCATION_NAME) == location_name for entry in existing_entries):
                errors[CONF_LOCATION_NAME] = "already_configured"

            # All validations passed, create entry
            if not errors:
                return self.async_create_entry(
                    title=f"Vicente Energy ({location_name})",
                    data=user_input
                )

        # Display form again with any accumulated errors
        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors
        )

class VicenteEnergyOptionsFlow(config_entries.OptionsFlow):
    """Handle an options flow to allow configuration changes for Vicente Energy."""
    def __init__(self, config_entry):
        """Initialize the OptionsFlow with the current config entry."""
        self.config_entry = config_entry
        self.reverse_name_map = {}

    async def async_step_init(self, user_input=None):
        """Handle the first step of the options flow."""
        if user_input is not None:
            # Only remap fields corresponding to service types
            service_keys = {stype.value for stype in ServiceType}

            translated_input = {
                key: self.reverse_name_map.get(value, value) if key in service_keys else value
                for key, value in user_input.items()
            }

            return self.async_create_entry(data=translated_input)

        loaded_integrations = await async_get_loaded_integrations(self.hass)
        loaded_domains = set(loaded_integrations.keys())

        schema_fields = {}
        self.reverse_name_map = {}

        for service_type in ServiceType:
            impls = SERVICE_CLASS_MAP.get(service_type, {})
            options = []

            for impl_key, cls in impls.items():
                domain = getattr(cls, "domain", None)
                if domain and domain in loaded_domains:
                    friendly = loaded_integrations[domain].name
                    options.append(friendly)
                    self.reverse_name_map[friendly] = impl_key

            if options:
                current_impl = self.config_entry.options.get(service_type.value)
                current_cls = impls.get(current_impl)
                current_domain = getattr(current_cls, "domain", None)
                default_friendly = (
                    loaded_integrations[current_domain].name
                    if current_domain in loaded_integrations
                    else sorted(options)[0]
                )

                schema_fields[
                    vol.Required(service_type.value, default=default_friendly)
                ] = vol.In(sorted(options))

        # Add additional optional configuration fields
        schema_fields[vol.Required(
            CONF_LOCATION_NAME,
            default=self.config_entry.options.get(CONF_LOCATION_NAME, "")
        )] = vol.All(str, vol.Length(max=32))

        schema_fields[vol.Required(
            CONF_BATTERY_CAPACITY_KWH,
            default=self.config_entry.options.get(CONF_BATTERY_CAPACITY_KWH, 15)
        )] = vol.All(float, vol.Range(min=0.1))

        schema_fields[vol.Required(
            CONF_RESERVE_SOC_PCT,
            default=self.config_entry.options.get(CONF_RESERVE_SOC_PCT, 20)
        )] = vol.All(int, vol.Range(min=0, max=100))

        schema_fields[vol.Required(
            CONF_STORAGE_EFFICIENCY,
            default=self.config_entry.options.get(CONF_STORAGE_EFFICIENCY, 0.90)
        )] = vol.All(float, vol.Range(min=0.0, max=1.0))

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(schema_fields)
        )

def get_available_implementations(service_type: ServiceType, loaded_integrations: set[str]) -> list[str]:
    """Return list of implementation names for a given service_type where the integration is loaded."""
    implementations = SERVICE_CLASS_MAP.get(service_type, {})
    return [
        impl_name
        for impl_name, cls in get_configured_integrations(self.hass).items()
        if getattr(cls, "domain", None) in loaded_integrations
    ]

async def async_get_loaded_integrations(hass) -> set[str]:
    """Return a set of all loaded integration domains and log them."""
    loaded_integrations = await async_get_integrations(hass)

    _LOGGER.info("Loaded integrations found:")
    for domain, integration in loaded_integrations.items():
        _LOGGER.info(" - %s (name: %s)", domain, integration.name)

    return set(loaded_integrations.keys())

def get_configured_integrations(hass) -> set[str]:
    """Return a set of domains with at least one ConfigEntry."""
    domains = set()
    for entry in hass.config_entries.async_entries():
        domains.add(entry.domain)
    return domains


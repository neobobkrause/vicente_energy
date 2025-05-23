"""Create and manage external service instances."""

import logging
import asyncio

from homeassistant.core import HomeAssistant

from .__init__ import SERVICE_CLASS_MAP, ServiceType
from .service import VEEntityStateChangeHandler, VEService

_LOGGER = logging.getLogger(__name__)

class ServiceManager:
    def __init__(self, hass: HomeAssistant, service_ids: dict[ServiceType, str]):
        """Initialize the ServiceManager with the named service types."""
        self._hass = hass
        self._services: dict[ServiceType, VEService] = {}

        self.update_services(service_ids, False)

        _LOGGER.debug("ServiceManager initialized with services: %s", self._services)

    async def connect_service(self, service_type: ServiceType):
        """Connect to external service."""
        service = self._services.get(service_type)
        if not service:
            raise ValueError(f"No services defined for service type '{service_type}'")

        await service.connect()
        _LOGGER.debug("Service %s connected successfully", service_type)

    async def disconnect_service(self, service_type: ServiceType):
        """Disconnect to external service."""
        service = self._services.get(service_type)
        if not service:
            raise ValueError(f"No services defined for service type '{service_type}'")

        await service.disconnect()
        _LOGGER.debug("Service %s disconnected successfully", service_type)

    async def connect_services(self):
        """Connect to external services asynchronously (if any)."""
        tasks = [service.connect() for service in self._services.values()]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for service_type, result in zip(self._services.keys(), results):
            if isinstance(result, Exception):
                _LOGGER.error("Service %s failed to connect: %s", service_type, result)
            else:
                _LOGGER.debug("Service %s connected successfully", service_type)

    async def disconnect_services(self):
        """Disconnect external services asynchronously (if any)."""
        tasks = [service.disconnect() for service in self._services.values()]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for service_type, result in zip(self._services.keys(), results):
            if isinstance(result, Exception):
                _LOGGER.error("Service %s failed to disconnect: %s", service_type, result)
            else:
                _LOGGER.debug("Service %s disconnected successfully", service_type)

    def update_services(self, service_ids: dict[ServiceType, str], connect: bool = True):
        """Dynamically update the service types and reinitialize services."""
        # Extract service types from the service_ids dictionary
        for service_type, service_name in service_ids.items():
            if service_name != self._services.get(service_type):
                # Get the valid service class mapping for this service type
                service_type_enum = ServiceType(service_type)
                valid_services = SERVICE_CLASS_MAP.get(service_type_enum)
                if not valid_services:
                    raise ValueError(f"No services defined for service type '{service_type}'")


                # Get the service class for the provided service name
                service_class = valid_services.get(service_name)
                if not service_class:
                    raise ValueError(
                        f"Service '{service_name}' is not valid for service type '{service_type}'. "
                        f"Valid options: {list(valid_services.keys())}"
                    )

                # Nothing to change if the existing service is the name as the new one
                existing_service = self._services.get(service_type)
                if existing_service is None or service_class != existing_service.__name__:
                    # Instantiate and store the service instance
                    self._services[service_type] = service_class()

                    # Optionally have the service instance connect
                    if connect:
                        service_class.connect()

    def get_service(self, service_type: ServiceType) -> VEService:
        service = self._services.get(service_type)
        if not service:
            raise ValueError(
                f"Service type '{service_type}' is not valid'. "
                f"Valid options: {list(self._services.keys())}"
            )
        return service

    def register_service_callback(self, service_type: ServiceType, cb: VEEntityStateChangeHandler):
        service: VEService = self.get_service(service_type)
        service.register_callback(cb)

    def deregister_service_callback(self, service_type: ServiceType,
                                    cb: VEEntityStateChangeHandler):
        service: VEService = self.get_service(service_type)
        service.deregister_callback(cb)

from typing import Optional
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import Entity


class EntityManager:
    """Centralized entity management for Vicente Energy integration."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        self.hass = hass
        self.entry = entry
        self.entities = {}

    async def async_setup_platforms(self):
        """Setup necessary platforms via Home Assistant's configuration entry."""
        await self.hass.config_entries.async_forward_entry_setups(self.entry, ["sensor"])

    async def async_unload_platforms(self):
        """Unload configured platforms via Home Assistant's configuration entry."""
        return await self.hass.config_entries.async_unload_platforms(self.entry, ["sensor"])

    async def register_entity(self, entity_id: str, entity_type: str,
                              unit: Optional[str], description: str):
        """Register and initialize a new entity within Home Assistant."""
        entity = VicenteEnergyEntity(entity_id, entity_type, unit, description)
        self.entities[entity_id] = entity
        self.hass.async_create_task(
            self.hass.helpers.entity_platform.async_add_entities([entity])
        )

    async def update_entity(self, entity_id: str, state, attributes: Optional[dict] = None):
        """Update the state and attributes of a managed entity."""
        entity = self.entities.get(entity_id)
        if entity:
            entity.set_state(state, attributes or {})
            await entity.async_update_ha_state()


class VicenteEnergyEntity(Entity):
    """Generic entity managed by Vicente Energy integration."""

    def __init__(self, entity_id: str, entity_type: str, unit: Optional[str], description: str):
        self._entity_id = f"{entity_type}.{entity_id}"
        self._unit_of_measurement = unit
        self._description = description
        self._state = None
        self._attributes = {}

    @property
    def name(self):
        return self._description

    @property
    def unique_id(self):
        return self._entity_id

    @property
    def state(self):
        return self._state

    @property
    def unit_of_measurement(self):
        return self._unit_of_measurement

    @property
    def extra_state_attributes(self):
        return self._attributes

    def set_state(self, state, attributes: dict):
        self._state = state
        self._attributes = attributes

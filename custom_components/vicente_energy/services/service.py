"""Shared base service object with entity state tracking."""

from abc import ABC
from typing import Callable
from typing import Optional
import logging

from homeassistant.core import HomeAssistant, State
from homeassistant.helpers.event import async_track_state_change

from ..const import DOMAIN
from ..entity_manager import EntityManager
from .service_manager import ServiceManager

VEEntityStateChangeHandler = Callable[[str, State, State], bool]

_LOGGER = logging.getLogger(__name__)

class VEService(ABC):
    """Base service class that manages callbacks and entity tracking."""

    def __init__(self, hass: HomeAssistant,
                 entity_handlers: Optional[dict[str, VEEntityStateChangeHandler]]) -> None:
        """Store Home Assistant instance and entity handlers."""
        self._hass: HomeAssistant = hass
        self._entity_handlers: Optional[dict[str, VEEntityStateChangeHandler]]\
            = entity_handlers  # Maps entity_id → handler
        self._callbacks: list[VEEntityStateChangeHandler] = []
        self._unsubs: list[Callable[[], None]] = []

    async def connect(self):
        """Begin tracking configured entities."""
        await self.set_handler_map(self._entity_handlers)

    async def disconnect(self):
        """Stop tracking entities and clear callbacks."""
        for unsub in self._unsubs:
            unsub()
        self._unsubs.clear()

    async def set_handler_map(self,
                              entity_handlers: Optional[dict[str, VEEntityStateChangeHandler]]):
        """Subscribe to state changes for the given entity map."""
        self._entity_handlers = entity_handlers  # Maps entity_id → handler

        if self._entity_handlers is not None:
            for entity_id in self._entity_handlers:
                unsub = async_track_state_change(
                    self._hass,
                    entity_id,
                    self._handle_state_change
                )
                self._unsubs.append(unsub)

    def _get_service_manager(self) -> ServiceManager:
        return self._hass.data[DOMAIN]["service_manager"]

    def _get_entity_manager(self) -> EntityManager:
        return self._hass.data[DOMAIN]["entity_manager"]

    def register_callback(self, callback: VEEntityStateChangeHandler) -> None:
        """Add a callback for state change notifications."""
        self._callbacks.append(callback)

    def deregister_callback(self, callback: VEEntityStateChangeHandler) -> None:
        """Deregister a previously registered callback."""
        try:
            self._callbacks.remove(callback)
            _LOGGER.debug("Callback %s deregistered successfully.", callback.__name__)
        except ValueError:
            _LOGGER.warning("Attempted to deregister non-existent callback %s.",
                            callback.__name__)

    def _get_callbacks(self) -> list[VEEntityStateChangeHandler]:
        """Return the callbacks registered for state change notifications."""
        return self._callbacks

    def _notify_subscribers(self, entity_id: str, old_state: State, new_state: State) -> None:
        """ Notify external subscribers """
        for cb in self._callbacks:
            cb(entity_id, old_state, new_state)

    async def _handle_state_change(self,
                                   entity_id: str, old_state: State | None,
                                   new_state: State | None) -> None:
        """Internal callback for Home Assistant state change events."""
        if old_state is None or new_state is None:
            return

        if new_state.state == old_state.state:
            return

        # 🧠 Delegate update to the specific entity handler
        if self._entity_handlers is not None:
            handler = self._entity_handlers.get(entity_id)
            if handler and handler(entity_id, old_state, new_state):
                # Notify external subscribers
                self._notify_subscribers(entity_id, old_state, new_state)

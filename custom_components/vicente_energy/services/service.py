"""Shared base service object with entity state tracking."""

from abc import ABC
from collections.abc import Callable
from typing import Optional

from homeassistant.core import HomeAssistant, State
from homeassistant.helpers.event import async_track_state_change

VEEntityStateChangeHandler = Callable[[str, State, State], bool]

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

    def register_callback(self, callback: VEEntityStateChangeHandler) -> None:
        """Add a callback for state change notifications."""
        self._callbacks.append(callback)

    def deregister_callback(self, callback: VEEntityStateChangeHandler) -> None:
        """Deregister a previously registered callback."""
        try:
            self._callbacks.remove(callback)
            _LOGGER.debug(f"Callback {callback.__name__} deregistered successfully.")
        except ValueError:
            _LOGGER.warning(f"Attempted to deregister non-existent callback {callback.__name__}.")

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
                for cb in self._callbacks:
                    cb(entity_id, old_state, new_state)

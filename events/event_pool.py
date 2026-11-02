"""Event registration, shrine branching, and run-local consumption rules."""
import random
from typing import Callable, List, Type

from engine.event_pool_state import EventPoolState
from engine.random_streams import StreamRandom


class EventMetadata:
    def __init__(self, event_class: Type, event_id: str, acts: str | list[int] | int = 'shared', weight: int = 100,
                 requires_condition: Callable[[], bool] | None = None, is_unique: bool = False,
                 category: str = 'event', state_provider: Callable[[], EventPoolState] | None = None):
        if category not in {'event', 'shrine', 'special', 'excluded'}:
            raise ValueError(f'Unknown event category: {category}')
        self.event_class = event_class
        self.event_id = event_id
        self.acts = acts
        self.weight = weight
        self.requires_condition = requires_condition
        self.category = category
        self.is_unique = is_unique or category == 'special'
        self._state_provider = state_provider
        self._standalone_used = False

    @property
    def has_been_used(self) -> bool:
        if self._state_provider is None:
            return self._standalone_used
        state = self._state_provider()
        used = state.used_once if self.is_unique else state.used_in_act
        return self.event_id in used

    @has_been_used.setter
    def has_been_used(self, value: bool) -> None:
        if self._state_provider is None:
            self._standalone_used = value
            return
        state = self._state_provider()
        used = state.used_once if self.is_unique else state.used_in_act
        if value:
            used.add(self.event_id)
        else:
            used.discard(self.event_id)


class EventPool:
    """Registry shared by definitions; usage and RNG belong to a single run."""
    SHRINE_CHANCE = 0.25

    def __init__(self, seed: int = 0, rng: random.Random | StreamRandom | None = None,
                 state_provider: Callable[[], EventPoolState] | None = None):
        self._event_registry: dict[str, EventMetadata] = {}
        self._state = EventPoolState(seed, rng)
        self._state_provider = state_provider

    def _get_state(self) -> EventPoolState:
        return self._state_provider() if self._state_provider is not None else self._state

    def register_event(self, event_class: Type, event_id: str, acts: str | list[int] | int = 'shared', weight: int = 100,
                       requires_condition: Callable[[], bool] | None = None, is_unique: bool = False,
                       category: str = 'event'):
        self._event_registry[event_id] = EventMetadata(
            event_class, event_id, acts, weight, requires_condition, is_unique,
            category, self._get_state,
        )

    @staticmethod
    def _matches_act(metadata: EventMetadata, act: int) -> bool:
        return act in (1, 2, 3) and (metadata.acts == 'shared' or
                metadata.acts == act or isinstance(metadata.acts, list) and act in metadata.acts)

    def _is_event_available(self, metadata: EventMetadata, act: int | None = None) -> bool:
        state = self._get_state()
        act = state.current_act if act is None else act
        if metadata.category == 'excluded' or metadata.weight <= 0:
            return False
        if metadata.is_unique:
            if metadata.event_id in state.used_once:
                return False
        elif act == state.current_act and metadata.event_id in state.used_in_act:
            return False
        can_appear = getattr(metadata.event_class, 'can_appear', None)
        if callable(can_appear) and not can_appear():
            return False
        return metadata.requires_condition is None or bool(metadata.requires_condition())

    def get_available_events(self, act: int = 1) -> List[EventMetadata]:
        # Sorting avoids hash-order-dependent seeded results. This query consumes nothing.
        return [metadata for _, metadata in sorted(self._event_registry.items())
                if self._matches_act(metadata, act) and self._is_event_available(metadata, act)]

    def draw_metadata(self, act: int = 1) -> EventMetadata | None:
        if act not in (1, 2, 3):
            return None
        state = self._get_state()
        state.enter_act(act)
        available = self.get_available_events(act)
        if not available:
            return None
        shrines = [m for m in available if m.category in ('shrine', 'special')]
        events = [m for m in available if m.category == 'event']
        primary, fallback = (shrines, events) if state.rng.random() < self.SHRINE_CHANCE else (events, shrines)
        candidates = primary or fallback
        if not candidates:
            return None
        selected = state.rng.choices(candidates, weights=[m.weight for m in candidates], k=1)[0]
        self.mark_event_used(selected.event_id)
        return selected

    def get_random_event(self, act: int = 1) -> Type | None:
        selected = self.draw_metadata(act)
        return selected.event_class if selected is not None else None

    def get_event_by_id(self, event_id: str) -> Type | None:
        metadata = self._event_registry.get(event_id)
        return metadata.event_class if metadata is not None else None

    def mark_event_used(self, event_id: str):
        metadata = self._event_registry.get(event_id)
        if metadata is not None:
            metadata.has_been_used = True

    def reset_unique_events(self):
        """Legacy new-run reset; chapter transitions use EventPoolState.enter_act."""
        self._get_state().reset()

    def get_events_by_act(self, act: int) -> List[str]:
        return sorted(key for key, metadata in self._event_registry.items()
                      if self._matches_act(metadata, act) and metadata.category != 'excluded')

    def get_all_registered_events(self) -> dict[str, EventMetadata]:
        return self._event_registry.copy()


def _current_run_state() -> EventPoolState:
    # Lazy import keeps registry creation independent of GameState initialization.
    from engine.game_state import game_state
    return game_state.event_pool_state


event_pool = EventPool(state_provider=_current_run_state)


def register_event(event_id: str, acts: str | list[int] | int = 'shared', weight: int = 100,
                   requires_condition: Callable[[], bool] | None = None,
                   is_unique: bool = False, category: str = 'event'):
    def decorator(event_class: Type) -> Type:
        event_pool.register_event(event_class, event_id, acts, weight,
                                  requires_condition, is_unique, category)
        return event_class
    return decorator

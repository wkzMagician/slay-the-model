"""
Events package initialization.

This module imports all event classes to register them to the event pool.
"""
from events.base_event import Event, CombatEvent
from events.neo_event import NeoEvent
from events.event_pool import event_pool, register_event

# Import all events to ensure they are registered
# When adding new events, import them here
__all__ = [
    'Event',
    'CombatEvent',
    'NeoEvent',
    'event_pool',
    'register_event'
]

# Events are automatically registered via the @register_event decorator
# when this module is imported
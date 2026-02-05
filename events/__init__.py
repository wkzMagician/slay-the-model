"""
Events package initialization.
"""
from events.base_event import Event, CombatEvent
from events.neo_event import NeoEvent
from events.event_pool import event_pool, register_event

# Import all events to ensure they are registered
from . import big_fish
from . import the_cleric
from . import house_of_god
from . import the_shrine
from . import woman_in_blue

__all__ = [
    'Event',
    'CombatEvent',
    'NeoEvent',
    'event_pool',
    'big_fish',
    'the_cleric',
    'house_of_god',
    'the_shrine',
    'woman_in_blue',
    'register_event'
]

# Events are automatically registered via the @register_event decorator
# when this module is imported
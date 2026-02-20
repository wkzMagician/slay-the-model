"""
Events package initialization.
All Slay the Spire events implemented based on wiki documentation.
"""
from events.base_event import Event
from events.combat_event import CombatEvent
from events.neo_event import NeoEvent
from events.event_pool import event_pool, register_event

# ============================================================================
# SHRINE EVENTS (All Acts)
# ============================================================================
from . import a_note_for_yourself
from . import bonfire_spirits
from . import duplicator
from . import divine_fountain
from . import golden_shrine
from . import lab
from . import match_and_keep
from . import ominous_forge
from . import purifier
from . import transmogrifier
from . import upgrade_shrine
from . import we_meet_again
from . import wheel_of_change
from . import woman_in_blue

# ============================================================================
# ACT 1 EVENTS
# ============================================================================
from . import big_fish
from . import dead_adventurer
from . import face_trader
from . import golden_idol
from . import hypnotizing_mushrooms
from . import living_wall
from . import scrap_ooze
from . import shining_light
from . import the_cleric
from . import the_ssssserpent
from . import wing_statue
from . import world_of_goop

# ============================================================================
# ACT 2 EVENTS
# ============================================================================
from . import ancient_writing
from . import augmenter
from . import council_of_ghosts
from . import cursed_tome
from . import designer_in_spire
from . import forgotten_altar
from . import knowing_skull
from . import masked_bandits
from . import nloth
from . import old_beggar
from . import pleading_vagrant
from . import the_colosseum
from . import the_joust
from . import the_library
from . import the_mausoleum
from . import the_nest
from . import vampires

# ============================================================================
# ACT 3 EVENTS
# ============================================================================
from . import falling
from . import mind_bloom
from . import mysterious_sphere
from . import secret_portal
from . import sensory_stone
from . import the_moai_head
from . import tomb_of_lord_red_mask
from . import winding_halls

# Legacy imports (keep for backwards compatibility)
from . import house_of_god
from . import the_shrine

__all__ = [
    'Event',
    'CombatEvent',
    'NeoEvent',
    'event_pool',
    'register_event',
    # Shrine Events
    'a_note_for_yourself',
    'bonfire_spirits',
    'duplicator',
    'divine_fountain',
    'golden_shrine',
    'lab',
    'match_and_keep',
    'ominous_forge',
    'purifier',
    'transmogrifier',
    'upgrade_shrine',
    'we_meet_again',
    'wheel_of_change',
    'woman_in_blue',
    # Act 1 Events
    'big_fish',
    'dead_adventurer',
    'face_trader',
    'golden_idol',
    'hypnotizing_mushrooms',
    'living_wall',
    'scrap_ooze',
    'shining_light',
    'the_cleric',
    'the_ssssserpent',
    'wing_statue',
    'world_of_goop',
    # Act 2 Events
    'ancient_writing',
    'augmenter',
    'council_of_ghosts',
    'cursed_tome',
    'designer_in_spire',
    'forgotten_altar',
    'knowing_skull',
    'masked_bandits',
    'nloth',
    'old_beggar',
    'pleading_vagrant',
    'the_colosseum',
    'the_joust',
    'the_library',
    'the_mausoleum',
    'the_nest',
    'vampires',
    # Act 3 Events
    'falling',
    'mind_bloom',
    'mysterious_sphere',
    'secret_portal',
    'sensory_stone',
    'the_moai_head',
    'tomb_of_lord_red_mask',
    'winding_halls',
    # Legacy
    'house_of_god',
    'the_shrine',
]

# Events are automatically registered via the @register_event decorator
# when this module is imported
"""
Ironclad's Heavy Blade card
"""
from cards.base import Card
from utils.registry import register
from utils.types import RarityType

@register("card")
class HeavyBlade(Card):
    """Deal damage, Strength affects this multiple times"""
    
    # Card attributes
    card_type = "Attack"
    rarity = RarityType.COMMON
    
    # Card values
    base_cost = 2
    base_damage = 14
    base_magic = {"strength_mult": 3}
    
    # Upgrade values
    upgrade_damage = 17
    upgrade_magic = {"strength_mult": 5}

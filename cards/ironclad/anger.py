"""
Ironclad's Anger card
"""
from cards.base import Card
from utils.registry import register
from utils.types import RarityType

@register("card")
class Anger(Card):
    """Deal damage and add a copy to discard pile"""
    
    # Card attributes
    card_type = "Attack"
    rarity = RarityType.STARTER
    
    # Card values
    base_cost = 0
    base_damage = 6
    base_draw = 0  # Will add copy to discard via magic
    
    # Upgrade values
    upgrade_damage = 8

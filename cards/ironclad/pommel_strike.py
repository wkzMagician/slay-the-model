"""
Ironclad's Pommel Strike card
"""
from cards.base import Card
from utils.registry import register
from utils.types import RarityType

@register("card")
class PommelStrike(Card):
    """Deal damage and draw cards"""
    
    # Card attributes
    card_type = "Attack"
    rarity = RarityType.COMMON
    
    # Card values
    base_cost = 1
    base_damage = 9
    base_draw = 1
    
    # Upgrade values
    upgrade_damage = 10
    upgrade_draw = 2

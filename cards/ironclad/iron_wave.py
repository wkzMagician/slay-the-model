"""
Ironclad's Iron Wave card
"""
from cards.base import Card
from utils.registry import register
from utils.types import RarityType

@register("card")
class IronWave(Card):
    """Gain block and deal damage"""
    
    # Card attributes
    card_type = "Attack"
    rarity = RarityType.COMMON
    
    # Card values
    base_cost = 1
    base_block = 5
    base_damage = 5
    
    # Upgrade values
    upgrade_block = 7
    upgrade_damage = 7

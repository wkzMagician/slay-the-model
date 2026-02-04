"""
Ironclad's Clothesline card
"""
from cards.base import Card
from utils.registry import register
from utils.types import RarityType

@register("card")
class Clothesline(Card):
    """Deal damage and apply Weak"""
    
    # Card attributes
    card_type = "Attack"
    rarity = RarityType.UNCOMMON
    
    # Card values
    base_cost = 2
    base_damage = 12
    base_magic = {"weak": 2}
    
    # Upgrade values
    upgrade_damage = 14
    upgrade_magic = {"weak": 3}

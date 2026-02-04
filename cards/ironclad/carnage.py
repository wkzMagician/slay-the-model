"""
Ironclad's Carnage card
"""
from cards.base import Card
from utils.registry import register
from utils.types import RarityType

@register("card")
class Carnage(Card):
    """Deal massive damage to all enemies"""
    
    # Card attributes
    card_type = "Attack"
    rarity = RarityType.UNCOMMON
    
    # Card values
    base_cost = 2
    base_damage = 20
    base_magic = {"aoe": 1}
    
    # Upgrade values
    upgrade_damage = 28

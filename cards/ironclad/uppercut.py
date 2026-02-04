"""
Ironclad's Uppercut card
"""
from cards.base import Card
from utils.registry import register
from utils.types import RarityType

@register("card")
class Uppercut(Card):
    """Deal damage and apply Vulnerable and Weak"""
    
    # Card attributes
    card_type = "Attack"
    rarity = RarityType.RARE
    
    # Card values
    base_cost = 2
    base_damage = 13
    base_magic = {"vulnerable": 2, "weak": 1}
    
    # Upgrade values
    upgrade_damage = 15
    upgrade_magic = {"vulnerable": 2, "weak": 2}

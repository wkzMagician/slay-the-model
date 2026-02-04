"""
Ironclad's Limit Break card
"""
from cards.base import Card
from utils.registry import register
from utils.types import RarityType

@register("card")
class LimitBreak(Card):
    """Double your Strength"""
    
    # Card attributes
    card_type = "Skill"
    rarity = RarityType.RARE
    
    # Card values
    base_cost = 1
    base_magic = {"double_strength": 1}
    
    # Upgrade values
    upgrade_cost = 0

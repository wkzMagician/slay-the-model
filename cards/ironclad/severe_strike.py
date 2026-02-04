"""
Ironclad's Severe Strike card
"""
from cards.base import Card
from utils.registry import register
from utils.types import RarityType

@register("card")
class SevereStrike(Card):
    """Deal heavy damage"""
    
    # Card attributes
    card_type = "Attack"
    rarity = RarityType.UNCOMMON
    
    # Card values
    base_cost = 2
    base_damage = 16
    
    # Upgrade values
    upgrade_damage = 20

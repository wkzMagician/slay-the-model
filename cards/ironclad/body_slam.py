"""
Ironclad's Body Slam card
"""
from cards.base import Card
from utils.registry import register
from utils.types import RarityType

@register("card")
class BodySlam(Card):
    """Deal damage equal to your block"""
    
    # Card attributes
    card_type = "Attack"
    rarity = RarityType.UNCOMMON
    
    # Card values
    base_cost = 1
    base_magic = {"damage_equals_block": 1}
    
    # Upgrade values
    upgrade_cost = 0

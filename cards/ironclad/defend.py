"""
Ironclad's Defend card
"""
from cards.base import Card
from utils.registry import register
from utils.types import RarityType

@register("card")
class Defend(Card):
    """Gain block"""
    
    # Card attributes
    card_type = "Skill"
    rarity = RarityType.STARTER
    
    # Card values
    base_cost = 1
    base_block = 5
    
    # Upgrade values
    upgrade_block = 8

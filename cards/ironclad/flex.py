"""
Ironclad's Flex card
"""
from cards.base import Card
from utils.registry import register
from utils.types import RarityType

@register("card")
class Flex(Card):
    """Gain Strength, lose it at end of turn"""
    
    # Card attributes
    card_type = "Power"
    rarity = RarityType.COMMON
    
    # Card values
    base_cost = 0
    base_magic = {"temp_strength": 2}
    
    # Upgrade values
    upgrade_magic = {"temp_strength": 4}

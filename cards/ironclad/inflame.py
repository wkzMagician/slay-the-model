"""
Ironclad's Inflame card
"""
from cards.base import Card
from utils.registry import register
from utils.types import RarityType

@register("card")
class Inflame(Card):
    """Gain Strength for this combat"""
    
    # Card attributes
    card_type = "Power"
    rarity = RarityType.UNCOMMON
    
    # Card values
    base_cost = 1
    base_magic = {"strength": 2}
    
    # Upgrade values
    upgrade_magic = {"strength": 3}

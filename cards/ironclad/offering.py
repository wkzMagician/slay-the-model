"""
Ironclad's Offering card
"""
from cards.base import Card
from utils.registry import register
from utils.types import RarityType

@register("card")
class Offering(Card):
    """Lose HP, gain Energy, Strength, and draw cards"""
    
    # Card attributes
    card_type = "Attack"
    rarity = RarityType.RARE
    
    # Card values
    base_cost = 0
    base_draw = 2
    base_energy_gain = 2
    base_magic = {"strength": 2, "lose_hp": 3}
    
    # Upgrade values
    upgrade_draw = 3
    upgrade_magic = {"strength": 2, "lose_hp": 0}

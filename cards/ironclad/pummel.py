"""
Ironclad's Pummel card
"""
from cards.base import Card
from utils.registry import register
from utils.types import RarityType

@register("card")
class Pummel(Card):
    """Deal damage multiple times"""
    
    # Card attributes
    card_type = "Attack"
    rarity = RarityType.RARE
    
    # Card values
    base_cost = 1
    base_damage = 2
    base_attack_times = 4
    
    # Upgrade values
    upgrade_attack_times = 5

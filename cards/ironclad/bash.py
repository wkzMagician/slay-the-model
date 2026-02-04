"""
Ironclad's Bash card
"""
from cards.base import Card
from utils.registry import register
from utils.types import RarityType

@register("card")
class Bash(Card):
    """Deal damage and apply Vulnerable"""
    
    # Card attributes
    card_type = "Attack"
    rarity = RarityType.STARTER
    
    # Card values
    base_cost = 2
    base_damage = 8
    base_magic = {"vulnerable": 2}
    
    # Upgrade values
    upgrade_damage = 10
    upgrade_magic = {"vulnerable": 3}

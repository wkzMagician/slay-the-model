"""
Ironclad's Armaments card
"""
from cards.base import Card
from utils.registry import register
from utils.types import RarityType

@register("card")
class Armaments(Card):
    """Gain block and upgrade a card in hand"""
    
    # Card attributes
    card_type = "Skill"
    rarity = RarityType.COMMON
    
    # Card values
    base_cost = 1
    base_block = 5
    base_magic = {"upgrade_hand": 0}
    
    # Upgrade values
    upgrade_block = 7
    upgrade_magic = {"upgrade_hand": 1}

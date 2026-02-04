"""
Ironclad's Bludgeon card
"""
from cards.base import Card
from utils.registry import register
from utils.types import RarityType

@register("card")
class Bludgeon(Card):
    """Deal massive damage and gain block (more if no block)"""
    
    # Card attributes
    card_type = "Attack"
    rarity = RarityType.RARE
    
    # Card values
    base_cost = 3
    base_damage = 32
    base_block = 5
    base_magic = {"block_if_no_block": 10}
    
    # Upgrade values
    upgrade_damage = 42
    upgrade_block = 7
    upgrade_magic = {"block_if_no_block": 13}

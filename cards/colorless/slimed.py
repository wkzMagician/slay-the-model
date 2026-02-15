"""
Slimed status card.
"""
from cards.base import Card
from utils.types import CardType, RarityType
from utils.registry import register


@register("card")
class Slimed(Card):
    """Unplayable. At the end of your turn, take 1 damage and discard this card."""
    
    card_type = CardType.STATUS
    rarity = RarityType.CURSE
    base_cost = 1  # Unplayable, cost is irrelevant
    base_block = 0
    base_damage = 0
    base_magic = {}
"""Silent uncommon attack card - Backstab."""

from cards.base import Card
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Backstab(Card):
    """Innate zero-cost attack."""

    card_type = CardType.ATTACK
    rarity = RarityType.UNCOMMON

    base_cost = 0
    base_damage = 11
    base_innate = True

    upgrade_damage = 15

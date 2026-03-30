"""Silent starter attack card - Strike."""

from cards.base import Card
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Strike(Card):
    """Deal damage."""

    card_type = CardType.ATTACK
    rarity = RarityType.STARTER

    base_cost = 1
    base_damage = 6

    upgrade_damage = 9

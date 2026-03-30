"""Silent common attack card - Slice."""

from cards.base import Card
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Slice(Card):
    """Deal damage for 0 energy."""

    card_type = CardType.ATTACK
    rarity = RarityType.COMMON

    base_cost = 0
    base_damage = 6

    upgrade_damage = 9

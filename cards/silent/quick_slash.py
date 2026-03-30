"""Silent common attack card - Quick Slash."""

from cards.base import Card
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class QuickSlash(Card):
    """Deal damage and draw a card."""

    card_type = CardType.ATTACK
    rarity = RarityType.COMMON

    base_cost = 1
    base_damage = 8
    base_draw = 1

    upgrade_damage = 12

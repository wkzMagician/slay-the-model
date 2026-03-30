"""Silent common skill card - Backflip."""

from cards.base import Card
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Backflip(Card):
    """Gain Block and draw cards."""

    card_type = CardType.SKILL
    rarity = RarityType.COMMON

    base_cost = 1
    base_block = 5
    base_draw = 2

    upgrade_block = 8

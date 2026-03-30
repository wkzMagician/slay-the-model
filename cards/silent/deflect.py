"""Silent common skill card - Deflect."""

from cards.base import Card
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Deflect(Card):
    """Gain block for 0 energy."""

    card_type = CardType.SKILL
    rarity = RarityType.COMMON

    base_cost = 0
    base_block = 4

    upgrade_block = 7

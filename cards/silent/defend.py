"""Silent starter skill card - Defend."""

from cards.base import Card
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Defend(Card):
    """Gain block."""

    card_type = CardType.SKILL
    rarity = RarityType.STARTER

    base_cost = 1
    base_block = 5

    upgrade_block = 8

"""Silent uncommon attack card - Dash."""

from cards.base import Card
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Dash(Card):
    """Deal damage and gain block."""

    card_type = CardType.ATTACK
    rarity = RarityType.UNCOMMON

    base_cost = 2
    base_damage = 10
    base_block = 10

    upgrade_damage = 13
    upgrade_block = 13

"""Defect common skill card - Boot Sequence."""

from cards.base import Card
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class BootSequence(Card):
    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON

    base_cost = 0
    base_block = 10
    base_innate = True
    base_exhaust = True

    upgrade_block = 13


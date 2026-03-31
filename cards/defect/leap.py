"""Defect common skill card - Leap."""

from cards.base import Card
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Leap(Card):
    card_type = CardType.SKILL
    rarity = RarityType.COMMON

    base_cost = 1
    base_block = 9
    upgrade_block = 12

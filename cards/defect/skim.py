"""Defect uncommon skill card - Skim."""

from cards.base import Card
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Skim(Card):
    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON

    base_cost = 1
    base_draw = 3
    upgrade_draw = 4

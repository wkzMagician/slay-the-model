"""Defect common attack card - Sweeping Beam."""

from cards.base import Card
from utils.registry import register
from utils.types import CardType, RarityType, TargetType


@register("card")
class SweepingBeam(Card):
    card_type = CardType.ATTACK
    rarity = RarityType.COMMON
    base_target_type = TargetType.ENEMY_ALL

    base_cost = 1
    base_damage = 6
    base_draw = 1
    upgrade_damage = 9

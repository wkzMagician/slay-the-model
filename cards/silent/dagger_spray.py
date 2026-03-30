"""Silent common attack card - Dagger Spray."""

from cards.base import Card
from utils.registry import register
from utils.types import CardType, RarityType, TargetType


@register("card")
class DaggerSpray(Card):
    """Deal damage to all enemies twice."""

    card_type = CardType.ATTACK
    rarity = RarityType.COMMON
    target_type = TargetType.ENEMY_ALL

    base_cost = 1
    base_damage = 4
    base_attack_times = 2

    upgrade_damage = 6

"""Silent rare attack card - Die Die Die."""

from cards.base import Card
from utils.registry import register
from utils.types import CardType, RarityType, TargetType


@register("card")
class DieDieDie(Card):
    """Deal damage to all enemies. Exhaust."""

    card_type = CardType.ATTACK
    rarity = RarityType.RARE
    target_type = TargetType.ENEMY_ALL

    base_cost = 1
    base_damage = 13
    base_exhaust = True

    upgrade_damage = 17

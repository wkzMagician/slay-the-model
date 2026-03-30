"""Silent uncommon attack card - Riddle With Holes."""

from cards.base import Card
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class RiddleWithHoles(Card):
    """Deal damage five times."""

    card_type = CardType.ATTACK
    rarity = RarityType.UNCOMMON

    base_cost = 2
    base_damage = 3
    base_attack_times = 5

    upgrade_damage = 4

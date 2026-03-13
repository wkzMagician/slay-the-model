"""
Ironclad Uncommon Attack card - Pummel
"""

from cards.base import Card
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Pummel(Card):
    """Deal damage multiple times"""

    card_type = CardType.ATTACK
    rarity = RarityType.UNCOMMON

    base_cost = 1
    base_damage = 2
    base_attack_times = 4

    base_exhaust = True

    upgrade_attack_times = 5

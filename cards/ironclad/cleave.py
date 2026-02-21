"""
Ironclad Common Attack card - Cleave
"""

from actions.base import Action
from entities.creature import Creature
from typing import List
from cards.base import Card
from utils.registry import register
from utils.types import CardType, RarityType, TargetType
from actions.combat import DealDamageAction


@register("card")
class Cleave(Card):
    """Deal damage to ALL enemies"""

    card_type = CardType.ATTACK
    rarity = RarityType.COMMON
    target_type = TargetType.ENEMY_ALL

    base_cost = 1
    base_damage = 8

    upgrade_damage = 11
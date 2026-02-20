"""
Ironclad Common Attack card - Thunderclap
"""

from typing import List
from actions.base import Action
from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType, TargetType


@register("card")
class Thunderclap(Card):
    """Deal damage and apply Vulnerable to ALL enemies"""

    card_type = CardType.ATTACK
    rarity = RarityType.COMMON
    target_type = TargetType.ENEMY_ALL

    base_cost = 1
    base_damage = 4

    upgrade_damage = 7

    def on_play(self, targets: List[Creature] = []) -> List[Action]:
        actions = super().on_play(targets)

        # Apply vulnerable debuff to all enemies
        for enemy in targets:
            if enemy.hp > 0:
                actions.append(ApplyPowerAction(target=enemy, power="vulnerable", amount=1))

        return actions

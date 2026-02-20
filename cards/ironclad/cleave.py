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

    def on_play(self, targets: List[Creature] = []) -> List[Action]:
        """Deal damage to ALL enemies"""
        from engine.game_state import game_state
        actions = []
        for enemy in targets:
            actions.append(DealDamageAction(target=enemy, damage=self.damage))
        return actions

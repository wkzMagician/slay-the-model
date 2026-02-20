"""
Ironclad Uncommon Attack card - Whirlwind
"""

from actions.base import Action
from entities.creature import Creature
from typing import List
from cards.base import Card
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Whirlwind(Card):
    """Deal damage to ALL enemies X times"""

    card_type = CardType.ATTACK
    rarity = RarityType.UNCOMMON

    base_cost = "X"  # X cost card
    base_damage = 5
    upgrade_damage = 8

    target_type = "ALL_ENEMIES"

    @property
    def attack_times(self) -> int:
        return self.cost  # feature: X药，+2

    def on_play(self, targets: List[Creature] = []) -> List[Action]:
        target = targets[0] if targets else None
        """Deal damage to ALL enemies X times."""
        from engine.game_state import game_state
        from actions.combat import DealDamageAction

        # X-cost: attack times = energy consumed (stored by test helper)
        times = getattr(self, '_x_cost_energy', 0)
        actions = []

        for enemy in game_state.combat.enemies:
            if enemy.hp > 0:
                for _ in range(times):
                    actions.append(DealDamageAction(
                        target=enemy,
                        damage=self.damage,
                        damage_type="attack",
                        card=self,
                    ))
        return actions
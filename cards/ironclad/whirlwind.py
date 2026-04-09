"""
Ironclad Uncommon Attack card - Whirlwind.
"""
from engine.runtime_api import add_action, add_actions

from typing import List

from actions.base import Action
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, DamageType, RarityType, TargetType


@register("card")
class Whirlwind(Card):
    """Deal damage to ALL enemies X times."""

    card_type = CardType.ATTACK
    rarity = RarityType.UNCOMMON

    base_cost = -1  # COST_X
    base_damage = 5
    upgrade_damage = 8

    target_type = TargetType.ENEMY_ALL

    @property
    def attack_times(self) -> int:
        from engine.game_state import game_state

        x_value = getattr(self, "_x_cost_energy", game_state.player.energy)
        has_chemical_x = any(
            getattr(relic, "idstr", None) == "ChemicalX"
            for relic in game_state.player.relics
        )
        return x_value + 2 if has_chemical_x else x_value

    def on_play(self, targets: List[Creature] = []):
        """Deal damage to all enemies X times."""
        from actions.combat import DealDamageAction
        from engine.game_state import game_state

        combat = game_state.combat
        if combat is None:
            return
        times = getattr(self, "_x_cost_energy", 0)
        has_chemical_x = any(
            getattr(relic, "idstr", None) == "ChemicalX"
            for relic in game_state.player.relics
        )
        if has_chemical_x:
            times += 2

        actions = []
        for enemy in combat.enemies:
            if enemy.hp <= 0:
                continue
            for _ in range(times):
                actions.append(
                    DealDamageAction(
                        target=enemy,
                        damage=self.damage,
                        damage_type=DamageType.PHYSICAL,
                        card=self,
                    )
                )
        from engine.game_state import game_state
        add_actions(actions)
        return

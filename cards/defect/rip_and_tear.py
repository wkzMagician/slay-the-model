"""Defect uncommon attack card - Rip and Tear."""

from typing import List

from actions.combat import AttackAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, DamageType, RarityType, TargetType


@register("card")
class RipAndTear(Card):
    card_type = CardType.ATTACK
    rarity = RarityType.UNCOMMON
    target_type = TargetType.ENEMY_RANDOM

    base_cost = 1
    base_damage = 7
    base_attack_times = 2
    upgrade_damage = 9

    def on_play(self, targets: List[Creature] = []):
        import random
        from engine.game_state import game_state
        from engine.runtime_api import add_action

        current_combat = game_state.current_combat
        if current_combat is None or game_state.player is None:
            return
        enemies = [enemy for enemy in current_combat.enemies if enemy.is_alive]
        for _ in range(self.attack_times):
            if not enemies:
                break
            add_action(AttackAction(damage=self.damage, target=random.choice(enemies), source=game_state.player, damage_type=DamageType.PHYSICAL, card=self))

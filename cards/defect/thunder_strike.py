"""Defect rare attack card - Thunder Strike."""

from typing import List

from actions.combat import AttackAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class ThunderStrike(Card):
    card_type = CardType.ATTACK
    rarity = RarityType.RARE

    base_cost = 3
    base_damage = 7
    upgrade_damage = 9

    @property
    def attack_times(self) -> int:
        from engine.game_state import game_state

        current_combat = getattr(game_state, "current_combat", None)
        if current_combat is None:
            return 0
        return current_combat.combat_state.orb_history.get("Lightning", 0)

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
            add_action(AttackAction(damage=self.damage, target=random.choice(enemies), source=game_state.player, damage_type="attack", card=self))

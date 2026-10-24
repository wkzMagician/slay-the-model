"""Defect rare attack card - Thunder Strike."""

from typing import List

from actions.combat_cards import RandomCardAttackAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType, TargetType


@register("card")
class ThunderStrike(Card):
    card_type = CardType.ATTACK
    rarity = RarityType.RARE
    target_type = TargetType.ENEMY_RANDOM

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
        from engine.game_state import game_state
        from engine.runtime_api import add_action

        if game_state.current_combat is None or game_state.player is None:
            return
        for _ in range(self.attack_times):
            add_action(RandomCardAttackAction(self, game_state.player))

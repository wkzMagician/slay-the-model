"""Defect common attack card - Barrage."""

from typing import List

from actions.combat import AttackAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, DamageType, RarityType


@register("card")
class Barrage(Card):
    card_type = CardType.ATTACK
    rarity = RarityType.COMMON

    base_cost = 1
    base_damage = 4
    upgrade_damage = 6

    @property
    def attack_times(self) -> int:
        from engine.game_state import game_state

        player = getattr(game_state, "player", None)
        if player is None:
            return 0
        return len(player.orb_manager.orbs)

    def on_play(self, targets: List[Creature] = []):
        from engine.game_state import game_state
        from engine.runtime_api import add_action

        target = targets[0] if targets else None
        if target is None:
            return
        for _ in range(self.attack_times):
            add_action(AttackAction(damage=self.damage, target=target, source=game_state.player, damage_type=DamageType.PHYSICAL, card=self))

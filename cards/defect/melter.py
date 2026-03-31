"""Defect uncommon attack card - Melter."""

from typing import List

from actions.base import LambdaAction
from actions.combat import AttackAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Melter(Card):
    card_type = CardType.ATTACK
    rarity = RarityType.UNCOMMON

    base_cost = 1
    base_damage = 10
    upgrade_damage = 14

    def on_play(self, targets: List[Creature] = []):
        from engine.game_state import game_state
        from engine.runtime_api import add_action

        if targets:
            target = targets[0]
            add_action(LambdaAction(func=lambda: setattr(target, "block", 0)))
            add_action(
                AttackAction(
                    damage=self.damage,
                    target=target,
                    source=game_state.player,
                    damage_type="attack",
                    card=self,
                )
            )

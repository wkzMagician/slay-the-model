"""Spire Spear Elite intentions for Act 4."""

import random
from typing import List

from actions.base import Action
from actions.card import AddCardAction
from actions.combat import ApplyPowerAction, AttackAction
from cards.colorless.burn import Burn
from enemies.intention import Intention
from utils.types import PilePosType


class BurnStrike(Intention):
    """Deal 5x2/6x2 and add 2 Burns to discard or draw pile."""

    def __init__(self, enemy):
        super().__init__("Burn Strike", enemy)

    def execute(self) -> List[Action]:
        from engine.game_state import game_state

        damage, hits, burn_pile = random.choice(
            [(5, 2, "discard_pile"), (6, 2, "discard_pile"),
             (6, 2, "draw_pile")]
        )

        actions = []
        for _ in range(hits):
            actions.append(
                AttackAction(
                    damage=damage,
                    target=game_state.player,
                    source=self.enemy,
                    damage_type="attack",
                )
            )

        for _ in range(2):
            actions.append(
                AddCardAction(
                    card=Burn(),
                    dest_pile=burn_pile,
                    position=PilePosType.TOP,
                )
            )
        return actions


class Skewer(Intention):
    """Deal 10 damage 3 times."""

    def __init__(self, enemy):
        super().__init__("Skewer", enemy)
        self.base_damage = 10
        self.hits = 3

    def execute(self) -> List[Action]:
        from engine.game_state import game_state

        actions = []
        for _ in range(self.hits):
            actions.append(
                AttackAction(
                    damage=self.base_damage,
                    target=game_state.player,
                    source=self.enemy,
                    damage_type="attack",
                )
            )
        return actions


class Piercer(Intention):
    """Deal 10x4 and sometimes grant all enemies +2 Strength."""

    def __init__(self, enemy):
        super().__init__("Piercer", enemy)
        self.base_damage = 10
        self.hits = 4

    def execute(self) -> List[Action]:
        from engine.game_state import game_state

        actions = []
        for _ in range(self.hits):
            actions.append(
                AttackAction(
                    damage=self.base_damage,
                    target=game_state.player,
                    source=self.enemy,
                    damage_type="attack",
                )
            )

        if random.choice([True, False]):
            combat = getattr(game_state, "current_combat", None) or getattr(
                game_state, "combat", None
            )
            if combat is not None:
                for enemy in combat.enemies:
                    if enemy.is_alive:
                        actions.append(
                            ApplyPowerAction(
                                power="Strength", target=enemy, amount=2
                            )
                        )

        return actions

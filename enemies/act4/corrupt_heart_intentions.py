"""Corrupt Heart boss intentions for Act 4."""

import random
from typing import List

from actions.base import Action, LambdaAction
from actions.card import AddCardAction
from actions.combat import ApplyPowerAction, AttackAction
from cards.colorless.burn import Burn
from cards.colorless.dazed import Dazed
from cards.colorless.slimed import Slimed
from cards.colorless.void import Void
from cards.colorless.wound import Wound
from enemies.intention import Intention
from powers.definitions.beat_of_death import BeatOfDeathPower
from powers.definitions.painful_stabs import PainfulStabsPower
from utils.types import PilePosType


class Debilitate(Intention):
    """Apply debuffs and shuffle status cards into draw pile."""

    def __init__(self, enemy):
        super().__init__("Debilitate", enemy)

    def execute(self) -> List[Action]:
        from engine.game_state import game_state
        player = game_state.player

        actions: List[Action] = [
            ApplyPowerAction(power="Vulnerable", target=player, amount=2),
            ApplyPowerAction(power="Weak", target=player, amount=2),
            ApplyPowerAction(power="Frail", target=player, amount=2),
        ]

        for status_cls in (Burn, Dazed, Slimed, Void, Wound):
            actions.append(
                AddCardAction(
                    card=status_cls(),
                    dest_pile="draw_pile",
                    position=PilePosType.TOP,
                )
            )
        return actions


class BloodShots(Intention):
    """Deal 2x12 or 2x15 damage."""

    def __init__(self, enemy):
        super().__init__("Blood Shots", enemy)

    def execute(self) -> List[Action]:
        from engine.game_state import game_state

        base_damage, hits = random.choice([(2, 12), (2, 15)])
        actions: List[Action] = []
        for _ in range(hits):
            actions.append(
                AttackAction(
                    damage=base_damage,
                    target=game_state.player,
                    source=self.enemy,
                    damage_type="attack",
                )
            )
        return actions


class Echo(Intention):
    """Deal 40 or 45 damage."""

    def __init__(self, enemy):
        super().__init__("Echo", enemy)

    def execute(self) -> List[Action]:
        from engine.game_state import game_state

        base_damage = random.choice([40, 45])
        return [
            AttackAction(
                damage=base_damage,
                target=game_state.player,
                source=self.enemy,
                damage_type="attack",
            )
        ]


class BuffHeart(Intention):
    """Apply Corrupt Heart scaling buff sequence."""

    def __init__(self, enemy):
        super().__init__("Buff", enemy)

    def execute(self) -> List[Action]:
        self.enemy._buff_count += 1
        buff_count = self.enemy._buff_count

        actions: List[Action] = [
            LambdaAction(func=self._remove_negative_strength),
            ApplyPowerAction(power="Strength", target=self.enemy, amount=2),
        ]

        if buff_count == 1:
            actions.append(ApplyPowerAction(power="Artifact", target=self.enemy, amount=1))
        elif buff_count == 2:
            actions.append(LambdaAction(func=self._add_beat_of_death))
        elif buff_count == 3:
            actions.append(LambdaAction(func=self._add_painful_stabs))
        elif buff_count == 4:
            actions.append(ApplyPowerAction(power="Strength", target=self.enemy, amount=10))
        elif buff_count == 5:
            actions.append(ApplyPowerAction(power="Strength", target=self.enemy, amount=50))

        return actions

    def _remove_negative_strength(self):
        strength = self.enemy.get_power("Strength")
        if strength is not None and strength.amount < 0:
            self.enemy.remove_power("Strength")

    def _add_beat_of_death(self):
        beat = self.enemy.get_power("Beat of Death")
        if beat is None:
            self.enemy.add_power(BeatOfDeathPower(amount=1, owner=self.enemy))
        else:
            beat.amount += 1

    def _add_painful_stabs(self):
        if not self.enemy.has_power("Painful Stabs"):
            self.enemy.add_power(PainfulStabsPower(amount=1, owner=self.enemy))

"""Defect uncommon attack card - Bullseye."""

from typing import List

from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from powers.definitions.lock_on import LockOnPower
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Bullseye(Card):
    card_type = CardType.ATTACK
    rarity = RarityType.UNCOMMON

    base_cost = 1
    base_damage = 8
    base_magic = {"lock_on": 2}
    upgrade_damage = 11
    upgrade_magic = {"lock_on": 3}

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.runtime_api import add_action

        if targets:
            duration = self.get_magic_value("lock_on")
            add_action(ApplyPowerAction(LockOnPower(duration=duration, owner=targets[0]), targets[0]))

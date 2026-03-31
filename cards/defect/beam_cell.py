"""Defect common attack card - Beam Cell."""

from typing import List

from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from powers.definitions.vulnerable import VulnerablePower
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class BeamCell(Card):
    card_type = CardType.ATTACK
    rarity = RarityType.COMMON

    base_cost = 0
    base_damage = 3
    base_magic = {"vulnerable": 1}
    upgrade_damage = 4
    upgrade_magic = {"vulnerable": 2}

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.runtime_api import add_action

        if targets:
            target = targets[0]
            vuln = self.get_magic_value("vulnerable")
            add_action(ApplyPowerAction(VulnerablePower(amount=vuln, duration=vuln, owner=target), target))

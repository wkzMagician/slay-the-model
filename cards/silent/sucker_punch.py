"""Silent common attack card - Sucker Punch."""

from typing import List

from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from powers.definitions.weak import WeakPower
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class SuckerPunch(Card):
    """Deal damage and apply Weak."""

    card_type = CardType.ATTACK
    rarity = RarityType.COMMON

    base_cost = 1
    base_damage = 7
    base_magic = {"weak": 1}

    upgrade_damage = 9
    upgrade_magic = {"weak": 2}

    def on_play(self, targets: List[Creature] = []):
        target = targets[0] if targets else None
        super().on_play(targets)
        if target is None:
            return
        from engine.runtime_api import add_actions

        weak = self.get_magic_value("weak")
        add_actions([
            ApplyPowerAction(WeakPower(amount=weak, duration=weak, owner=target), target)
        ])

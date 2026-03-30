"""Silent starter attack card - Neutralize."""

from typing import List

from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from powers.definitions.weak import WeakPower
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Neutralize(Card):
    """Deal damage and apply Weak."""

    card_type = CardType.ATTACK
    rarity = RarityType.STARTER

    base_cost = 0
    base_damage = 3
    base_magic = {"weak": 1}

    upgrade_damage = 5
    upgrade_magic = {"weak": 2}

    def on_play(self, targets: List[Creature] = []):
        target = targets[0] if targets else None
        super().on_play(targets)
        if target is None:
            return

        weak_amount = self.get_magic_value("weak")
        from engine.runtime_api import add_actions

        add_actions([
            ApplyPowerAction(
                WeakPower(amount=weak_amount, duration=weak_amount, owner=target),
                target,
            )
        ])

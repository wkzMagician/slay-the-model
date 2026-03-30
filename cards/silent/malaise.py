"""Silent uncommon skill card - Malaise."""

from typing import List

from actions.combat import ApplyPowerAction
from cards.base import COST_X, Card
from entities.creature import Creature
from powers.definitions.strength import StrengthPower
from powers.definitions.weak import WeakPower
from utils.registry import register
from utils.types import CardType, RarityType, TargetType


@register("card")
class Malaise(Card):
    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON
    target_type = TargetType.ENEMY_SELECT

    base_cost = COST_X
    upgrade_cost = 0

    def on_play(self, targets: List[Creature] = []):
        target = targets[0] if targets else None
        if target is None:
            return
        from engine.runtime_api import add_actions

        x_value = getattr(self, '_x_cost_energy', 0)
        add_actions([
            ApplyPowerAction(WeakPower(amount=x_value, duration=x_value, owner=target), target),
            ApplyPowerAction(StrengthPower(amount=-x_value, owner=target), target),
        ])

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
    rarity = RarityType.RARE
    target_type = TargetType.ENEMY_SELECT

    base_cost = COST_X
    base_exhaust = True

    def on_play(self, targets: List[Creature] = []):
        target = targets[0] if targets else None
        if target is None:
            return
        from engine.runtime_api import add_actions

        x_value = self.get_effective_x() + self.upgrade_level
        add_actions([
            ApplyPowerAction(WeakPower(amount=x_value, duration=x_value, owner=target), target),
            ApplyPowerAction(StrengthPower(amount=-x_value, owner=target), target),
        ])

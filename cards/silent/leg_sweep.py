"""Silent uncommon skill card - Leg Sweep."""

from typing import List

from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from powers.definitions.weak import WeakPower
from utils.registry import register
from utils.types import CardType, RarityType, TargetType


@register("card")
class LegSweep(Card):
    """Gain block and apply Weak."""

    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON
    target_type = TargetType.ENEMY_SELECT

    base_cost = 2
    base_block = 11
    base_magic = {"weak": 2}

    upgrade_block = 14
    upgrade_magic = {"weak": 3}

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

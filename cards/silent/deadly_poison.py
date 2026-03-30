"""Silent common skill card - Deadly Poison."""

from typing import List

from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from powers.definitions.poison import PoisonPower
from utils.registry import register
from utils.types import CardType, RarityType, TargetType


@register("card")
class DeadlyPoison(Card):
    """Apply Poison."""

    card_type = CardType.SKILL
    rarity = RarityType.COMMON
    target_type = TargetType.ENEMY_SELECT

    base_cost = 1
    base_magic = {"poison": 5}
    upgrade_magic = {"poison": 7}

    def on_play(self, targets: List[Creature] = []):
        target = targets[0] if targets else None
        super().on_play(targets)
        if target is None:
            return
        from engine.runtime_api import add_actions

        poison = self.get_magic_value("poison")
        add_actions([
            ApplyPowerAction(PoisonPower(amount=poison, duration=poison, owner=target), target)
        ])

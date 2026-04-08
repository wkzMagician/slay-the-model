"""Silent uncommon skill card - Catalyst."""

from typing import List

from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType, TargetType


@register("card")
class Catalyst(Card):
    """Multiply an enemy's Poison."""

    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON
    target_type = TargetType.ENEMY_SELECT

    base_cost = 1
    base_exhaust = True
    base_magic = {"multiplier": 2}

    upgrade_magic = {"multiplier": 3}

    def on_play(self, targets: List[Creature] = []):
        target = targets[0] if targets else None
        super().on_play(targets)
        if target is None:
            return
        poison = target.get_power("Poison")
        if poison is None:
            return
        poison.duration *= self.get_magic_value("multiplier")

"""Silent uncommon skill card - Terror."""

from typing import List

from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from powers.definitions.vulnerable import VulnerablePower
from utils.registry import register
from utils.types import CardType, RarityType, TargetType


@register("card")
class Terror(Card):
    """Apply long-lasting Vulnerable."""

    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON
    target_type = TargetType.ENEMY_SELECT

    base_cost = 1
    base_magic = {"vulnerable": 99}

    upgrade_cost = 0

    def on_play(self, targets: List[Creature] = []):
        target = targets[0] if targets else None
        super().on_play(targets)
        if target is None:
            return
        from engine.runtime_api import add_actions

        vulnerable = self.get_magic_value("vulnerable")
        add_actions([
            ApplyPowerAction(VulnerablePower(amount=vulnerable, duration=vulnerable, owner=target), target)
        ])

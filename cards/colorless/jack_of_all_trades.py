"""
Colorless Uncommon Skill card - Jack of All Trades
"""

from typing import List
from actions.base import Action
from actions.card import AddRandomCardAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class JackOfAllTrades(Card):
    """Add random colorless card(s), Exhaust"""

    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON

    base_cost = 0
    base_magic = {"add_count": 1}
    base_exhaust = True

    upgrade_magic = {"add_count": 2}

    def on_play(self, targets: List[Creature] = []) -> List[Action]:
        target = targets[0] if targets else None
        actions = super().on_play(targets)

        # Add random colorless card(s)
        add_count = self.get_magic_value("add_count")
        for _ in range(add_count):
            actions.append(AddRandomCardAction(
                pile="hand",
                namespace="colorless"
            ))

        return actions

"""
Colorless Rare Skill card - Apotheosis
"""

from typing import List
from actions.base import Action
from actions.card import ChooseUpgradeCardAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Apotheosis(Card):
    """Upgrade ALL cards for this battle, Exhaust"""

    card_type = CardType.SKILL
    rarity = RarityType.RARE

    base_cost = 2
    base_exhaust = True

    upgrade_cost = 1

    def on_play(self, targets: List[Creature] = []) -> List[Action]:
        target = targets[0] if targets else None

        actions = super().on_play(targets)

        # Upgrade ALL cards for this battle
        # We need to upgrade all cards in deck, hand, draw, discard
        # For now, let's use ChooseUpgradeCardAction with -1 to upgrade all
        # Note: -1 in amount means upgrade all eligible cards
        actions.extend(
            [
                ChooseUpgradeCardAction(pile="hand", amount=-1),
                ChooseUpgradeCardAction(pile="draw_pile", amount=-1),
                ChooseUpgradeCardAction(pile="discard_pile", amount=-1)
            ]
        )

        return actions

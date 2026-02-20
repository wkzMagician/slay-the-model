"""
Colorless Uncommon Skill card - Purify
"""

from typing import List
from actions.base import Action
from actions.card import ChooseExhaustCardAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Purify(Card):
    """Exhaust up to cards, Exhaust"""

    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON

    base_cost = 0
    base_magic = {"exhaust_amount": 3}
    base_exhaust = True

    upgrade_magic = {"exhaust_amount": 5}

    def on_play(self, targets: List[Creature] = []) -> List[Action]:
        target = targets[0] if targets else None
        actions = super().on_play(targets)

        # Exhaust up to N cards
        exhaust_amount = self.get_magic_value("exhaust_amount")
        actions.append(ChooseExhaustCardAction(
            pile="hand",
            amount=exhaust_amount
        ))

        return actions

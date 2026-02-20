"""
Colorless Uncommon Skill card - Discovery
"""

from typing import List
from actions.base import Action
from actions.card import ChooseAddRandomCardAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Discovery(Card):
    """Choose 1 of 3 random cards, costs 0 this turn, Exhaust"""

    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON

    base_cost = 1
    base_exhaust = True
    upgrade_exhaust = False

    def on_play(self, targets: List[Creature] = []) -> List[Action]:
        target = targets[0] if targets else None
        actions = super().on_play(targets)

        # Choose 1 of 3 random cards
        actions.append(ChooseAddRandomCardAction(
            total=3,
            namespace="colorless",
            temp_cost=0  # Cards cost 0 this turn
        ))

        return actions

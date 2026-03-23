"""
Ironclad Rare Skill card - Exhume
"""

from typing import List
from actions.base import Action
from actions.card import ChooseMoveCardAction, ExhaustCardAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Exhume(Card):
    """Choose a card from your Exhaust pile and add it to your hand"""

    card_type = CardType.SKILL
    rarity = RarityType.RARE

    base_cost = 1
    base_exhaust = True
    upgrade_cost = 0

    def on_play(self, targets: List[Creature] = []) -> List[Action]:
        actions = super().on_play(targets)
        exhaust_actions = []
        other_actions = []

        for action in actions:
            if isinstance(action, ExhaustCardAction) and action.card is self:
                exhaust_actions.append(action)
            else:
                other_actions.append(action)

        return other_actions + [
            ChooseMoveCardAction(src="exhaust_pile", dst="hand", amount=1)
        ] + exhaust_actions

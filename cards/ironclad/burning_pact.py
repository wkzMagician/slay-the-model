"""
Ironclad Uncommon Skill card - Burning Pact
"""

from typing import List
from actions.base import Action
from actions.card import ChooseExhaustCardAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class BurningPact(Card):
    """Exhaust cards, draw for each"""

    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON

    base_cost = 1
    base_draw = 2
    upgrade_draw = 3

    def on_play(self, targets: List[Creature] = []) -> List[Action]:
        return [ChooseExhaustCardAction(pile='hand', amount=1)] + super().on_play(targets)

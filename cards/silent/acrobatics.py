"""Silent common skill card - Acrobatics."""

from typing import List

from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Acrobatics(Card):
    """Draw cards, then discard a card."""

    card_type = CardType.SKILL
    rarity = RarityType.COMMON

    base_cost = 1
    base_draw = 3

    upgrade_draw = 4

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from actions.card_choice import ChooseDiscardCardAction
        from engine.runtime_api import add_actions

        add_actions([
            ChooseDiscardCardAction(pile="hand", amount=1),
        ])

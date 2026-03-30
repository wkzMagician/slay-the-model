"""Silent common attack card - Dagger Throw."""

from typing import List

from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class DaggerThrow(Card):
    """Deal damage, draw a card, then discard a card."""

    card_type = CardType.ATTACK
    rarity = RarityType.COMMON

    base_cost = 1
    base_damage = 6
    base_draw = 1

    upgrade_damage = 9

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from actions.card_choice import ChooseDiscardCardAction
        from engine.runtime_api import add_actions

        add_actions([
            ChooseDiscardCardAction(pile="hand", amount=1),
        ])

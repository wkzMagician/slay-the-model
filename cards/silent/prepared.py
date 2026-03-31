"""Silent common skill card - Prepared."""

from typing import List

from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Prepared(Card):
    """Draw cards, then discard cards."""

    card_type = CardType.SKILL
    rarity = RarityType.COMMON

    base_cost = 0
    base_draw = 1
    base_magic = {"discard": 1}

    upgrade_draw = 2
    upgrade_magic = {"discard": 2}

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from actions.card_choice import ChooseDiscardCardAction
        from engine.runtime_api import add_actions

        add_actions([
            ChooseDiscardCardAction(pile="hand", amount=self.get_magic_value("discard")),
        ])

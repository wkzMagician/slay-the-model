"""
Ironclad Common Skill card - True Grit
"""

from typing import List
from actions.base import Action
from actions.combat import GainBlockAction
from actions.card import ChooseExhaustCardAction, ExhaustCardAction, ExhaustRandomCardAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class TrueGrit(Card):
    """Gain block and exhaust a random card"""

    card_type = CardType.SKILL
    rarity = RarityType.COMMON

    base_cost = 1
    base_block = 7

    upgrade_block = 9

    def on_play(self, target: Creature | None = None) -> List[Action]:
        from engine.game_state import game_state

        actions = super().on_play(target)

        # Exhaust random card (base) or choose card (upgraded)
        if self.upgrade_level == 0:
            actions.append(ExhaustRandomCardAction(pile="hand", amount=1))
        else:
            actions.append(ChooseExhaustCardAction(pile='hand', amount=1))

        return actions

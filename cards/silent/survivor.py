"""Silent starter skill card - Survivor."""

from engine.runtime_api import add_actions

from cards.base import Card
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Survivor(Card):
    """Gain block, then discard a card."""

    card_type = CardType.SKILL
    rarity = RarityType.STARTER

    base_cost = 1
    base_block = 8

    upgrade_block = 11

    def on_play(self, targets=[]):
        super().on_play(targets)
        from actions.card_choice import ChooseDiscardCardAction

        add_actions([
            ChooseDiscardCardAction(pile="hand", amount=1),
        ])

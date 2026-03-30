"""Silent uncommon skill card - Reflex."""

from actions.card import DrawCardsAction
from cards.base import COST_UNPLAYABLE, Card
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Reflex(Card):
    """Unplayable. When discarded, draw cards."""

    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON

    base_cost = COST_UNPLAYABLE
    base_magic = {"draw": 2}

    upgrade_magic = {"draw": 3}

    def on_discard(self):
        from engine.runtime_api import add_actions

        add_actions([DrawCardsAction(count=self.get_magic_value("draw"))])

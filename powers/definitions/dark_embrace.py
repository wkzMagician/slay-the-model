"""
Dark Embrace power for Ironclad.
Whenever a card is exhausted, draw 1 card.
"""
from typing import List, Any
from powers.base import Power
from actions.base import Action
from actions.card import DrawCardsAction
from utils.registry import register


@register("power")
class DarkEmbracePower(Power):
    """Whenever a card is exhausted, draw 1 card."""

    name = "Dark Embrace"
    description = "Whenever a card is exhausted, draw 1 card."
    stackable = True
    amount_equals_duration = False
    is_buff = True

    def __init__(self, amount: int = 0, duration: int = 0, owner=None):
        """
        Args:
            amount: card to draw
            duration: 0 for permanent
        """
        super().__init__(amount=amount, duration=-1, owner=owner)

    def on_exhaust(self) -> List[Action]:
        """Draw 1 card when any card is exhausted."""
        return [DrawCardsAction(count=self.amount)]

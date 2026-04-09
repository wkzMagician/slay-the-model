"""
Dark Embrace power for Ironclad.
Whenever a card is exhausted, draw 1 card.
"""
from engine.runtime_api import add_action, add_actions
from actions.card import DrawCardsAction
from powers.base import Power, StackType
from engine.messages import CardExhaustedMessage
from engine.subscriptions import MessagePriority, subscribe
from utils.registry import register


@register("power")
class DarkEmbracePower(Power):
    """Whenever a card is exhausted, draw 1 card."""

    name = "Dark Embrace"
    description = "Whenever a card is exhausted, draw 1 card."
    stack_type = StackType.INTENSITY
    is_buff = True

    def __init__(self, amount: int = 1, duration: int = -1, owner=None):
        """
        Args:
            amount: card to draw
            duration: 0 for permanent
        """
        super().__init__(amount=amount, duration=duration, owner=owner)

    @subscribe(CardExhaustedMessage, priority=MessagePriority.REACTION)
    def on_card_exhausted(self, card, source_pile=None):
        add_actions([DrawCardsAction(count=self.amount)])
        return

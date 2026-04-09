"""
Feel No Pain power for Ironclad.
Whenever you exhaust one card, gain block.
"""
from engine.runtime_api import add_action, add_actions
from actions.combat import GainBlockAction
from powers.base import Power, StackType
from engine.messages import CardExhaustedMessage
from engine.subscriptions import MessagePriority, subscribe
from utils.registry import register


@register("power")
class FeelNoPainPower(Power):
    """Whenever you exhaust one card, gain 3/4 block."""

    name = "Feel No Pain"
    description = "Whenever you exhaust one card, gain block."
    stack_type = StackType.INTENSITY
    is_buff = True

    def __init__(self, amount: int = 3, duration: int = -1, owner=None):
        """
        Args:
            amount: Block to gain per exhaust (default 3)
            duration: 0 for permanent
        """
        super().__init__(amount=amount, duration=duration, owner=owner)

    @subscribe(CardExhaustedMessage, priority=MessagePriority.REACTION)
    def on_card_exhausted(self, card, source_pile=None):
        add_actions([GainBlockAction(block=self.amount, target=self.owner)])
        return

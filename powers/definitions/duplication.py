"""
Duplication power for combat effects.
Your next cards are played twice.
"""
from cards.base import Card
from powers.base import Power, StackType
from utils.registry import register

@register("power")
class DuplicationPower(Power):
    """Your next X cards are played twice."""
    
    name = "Duplication"
    description = "Your next cards are played twice."
    stack_type = StackType.INTENSITY
    is_buff = True  # Beneficial effect - plays cards twice
    
    def __init__(self, amount: int = 1, duration: int = -1, owner=None):
        """
        Args:
            amount: Number of cards to duplicate (default 1)
            duration: 0 for permanent, positive for temporary turns
        """
        super().__init__(amount=amount, duration=duration, owner=owner)

    def on_card_play(self, card: Card, targets):
        if getattr(card, "_is_replay", False) or self.amount <= 0:
            return
        from actions.autoplay import queue_replay
        queue_replay(card)
        self.amount -= 1
        if self.owner is not None and self.amount <= 0:
            self.owner.remove_power(self.name)

    def on_turn_end(self):
        super().on_turn_end()
        self.amount -= 1
        if self.owner is not None and self.amount <= 0:
            self.owner.remove_power(self)

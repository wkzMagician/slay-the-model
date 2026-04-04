"""Equilibrium power — retain non-Ethereal hand at end of player turn (matches STS EquilibriumPower)."""

from powers.base import Power, StackType
from utils.registry import register


@register("power")
class EquilibriumPower(Power):
    name = "Equilibrium"
    description = "At the end of your turn, retain your hand."
    stack_type = StackType.INTENSITY
    is_buff = True

    def __init__(self, amount: int = 1, duration: int = -1, owner=None):
        super().__init__(amount=amount, duration=duration, owner=owner)

    def on_turn_end(self):
        if self.owner is None:
            return
        cm = getattr(self.owner, "card_manager", None)
        if not cm:
            return
        for card in list(cm.get_pile("hand")):
            if not getattr(card, "ethereal", False):
                setattr(card, "retain_this_turn", True)
        self.amount -= 1
        if self.amount <= 0:
            self.owner.remove_power(self.name)

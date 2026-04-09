"""Defect Echo Form power."""

from powers.base import Power, StackType
from utils.registry import register


@register("power")
class EchoFormPower(Power):
    name = "Echo Form"
    description = "The first card you play each turn is played twice."
    stack_type = StackType.INTENSITY
    is_buff = True

    def __init__(self, amount: int = 1, duration: int = -1, owner=None):
        super().__init__(amount=amount, duration=duration, owner=owner)
        self.cards_left_this_turn = amount

    def on_turn_start(self):
        self.cards_left_this_turn = self.amount

    def on_card_play(self, card, targets):
        if self.cards_left_this_turn <= 0:
            return
        card.on_play(targets=targets or [])
        self.cards_left_this_turn -= 1

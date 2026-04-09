"""Defect Amplify power."""

from powers.base import Power, StackType
from utils.registry import register
from utils.types import CardType


@register("power")
class AmplifyPower(Power):
    name = "Amplify"
    description = "This turn, your next {amount} Power card(s) are played twice."
    stack_type = StackType.INTENSITY
    is_buff = True

    def __init__(self, amount: int = 1, duration: int = 1, owner=None):
        super().__init__(amount=amount, duration=duration, owner=owner)

    def on_card_play(self, card, targets):
        if getattr(card, "card_type", None) != CardType.POWER:
            return
        card.on_play(targets=targets or [])
        self.amount -= 1
        if self.owner is not None and self.amount <= 0:
            self.owner.remove_power(self.name)

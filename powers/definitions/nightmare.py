"""Nightmare delayed copy power."""

from actions.card import AddCardAction
from powers.base import Power, StackType
from utils.registry import register


@register("power")
class NightmarePower(Power):
    name = 'Nightmare'
    description = 'At the start of next turn, add 3 copies of a chosen card into your hand.'
    stack_type = StackType.MULTI_INSTANCE
    is_buff = True

    def __init__(self, amount: int = 3, duration: int = 2, owner=None, stored_card=None):
        super().__init__(amount=amount, duration=duration, owner=owner)
        self.stored_card = stored_card

    def on_turn_start(self):
        from engine.runtime_api import add_actions

        if self.owner is not None and self.stored_card is not None:
            add_actions([AddCardAction(card=self.stored_card.copy(), dest_pile='hand') for _ in range(self.amount)])
            self.owner.remove_power(self.name)

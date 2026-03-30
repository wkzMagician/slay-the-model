"""Silent power - Infinite Blades."""

from actions.card import AddCardAction
from engine.runtime_api import add_actions
from powers.base import Power, StackType
from utils.registry import register


@register("power")
class InfiniteBladesPower(Power):
    name = "Infinite Blades"
    description = "At the start of your turn, add 1 Shiv into your hand."
    stack_type = StackType.PRESENCE
    is_buff = True

    def __init__(self, amount: int = 1, duration: int = -1, owner=None):
        super().__init__(amount=amount, duration=duration, owner=owner)

    def on_turn_start(self):
        from cards.colorless.shiv import Shiv

        add_actions([AddCardAction(card=Shiv(), dest_pile="hand")])
        return

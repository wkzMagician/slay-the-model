"""One-shot Escape Plan check power."""

from actions.combat import GainBlockAction
from powers.base import Power, StackType
from utils.registry import register
from utils.types import CardType


@register("power")
class EscapePlanCheckPower(Power):
    name = "Escape Plan Check"
    description = "The next drawn card determines whether Escape Plan grants Block."
    stack_type = StackType.PRESENCE
    is_buff = True

    def __init__(self, amount: int = 3, duration: int = 1, owner=None):
        super().__init__(amount=amount, duration=duration, owner=owner)

    def on_card_draw(self, card):
        from engine.runtime_api import add_actions

        if self.owner is not None and getattr(card, 'card_type', None) == CardType.SKILL:
            add_actions([GainBlockAction(block=self.amount, target=self.owner)])
        if self.owner is not None:
            self.owner.remove_power(self.name)

"""Well-Laid Plans retain power."""

from actions.card_choice import ChooseRetainCardAction
from powers.base import Power, StackType
from utils.registry import register


@register("power")
class WellLaidPlansPower(Power):
    name = 'Well-Laid Plans'
    description = 'At the end of your turn, retain cards.'
    stack_type = StackType.INTENSITY
    is_buff = True

    def __init__(self, amount: int = 1, duration: int = -1, owner=None):
        super().__init__(amount=amount, duration=duration, owner=owner)

    def on_turn_end(self):
        from engine.runtime_api import add_actions
        if self.owner is None:
            return
        add_actions([ChooseRetainCardAction(amount=self.amount)])

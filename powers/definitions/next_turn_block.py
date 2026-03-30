"""Next Turn Block power for delayed block gain."""
from engine.runtime_api import add_actions
from actions.base import LambdaAction
from actions.combat import GainBlockAction
from powers.base import Power, StackType
from utils.registry import register


@register("power")
class NextTurnBlockPower(Power):
    """Gain block at the start of your next turn."""

    name = "Next Turn Block"
    description = "Gain block at the start of your next turn."
    stack_type = StackType.INTENSITY
    is_buff = True

    def __init__(self, amount: int = 1, duration: int = 1, owner=None):
        super().__init__(amount=amount, duration=duration, owner=owner)

    def on_turn_start(self):
        if self.owner is None:
            return
        add_actions([
            GainBlockAction(block=self.amount, target=self.owner),
            LambdaAction(func=lambda: self.owner.remove_power(self.name)),
        ])
        return

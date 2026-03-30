"""Energized power for delayed energy gain next turn."""
from engine.runtime_api import add_actions
from actions.base import LambdaAction
from actions.combat import GainEnergyAction
from powers.base import Power, StackType
from utils.registry import register


@register("power")
class EnergizedPower(Power):
    """Gain energy at the start of your next turn."""

    name = "Energized"
    description = "Gain energy at the start of your next turn."
    stack_type = StackType.INTENSITY
    is_buff = True

    def __init__(self, amount: int = 1, duration: int = 1, owner=None):
        super().__init__(amount=amount, duration=duration, owner=owner)

    def on_turn_start(self):
        if self.owner is None:
            return
        add_actions([
            GainEnergyAction(energy=self.amount),
            LambdaAction(func=lambda: self.owner.remove_power(self.name)),
        ])
        return

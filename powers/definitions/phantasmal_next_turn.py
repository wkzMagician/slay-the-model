"""Delayed Phantasmal Killer setup power."""

from actions.combat import ApplyPowerAction
from powers.base import Power, StackType
from powers.definitions.phantasmal_killer import PhantasmalKillerPower
from utils.registry import register


@register("power")
class PhantasmalNextTurnPower(Power):
    name = "Phantasmal Killer Next Turn"
    description = "At the start of next turn, your attacks deal double damage."
    stack_type = StackType.PRESENCE
    is_buff = True

    def __init__(self, amount: int = 2, duration: int = 1, owner=None):
        super().__init__(amount=amount, duration=duration, owner=owner)

    def on_turn_start(self):
        from engine.runtime_api import add_actions

        if self.owner is not None:
            add_actions([ApplyPowerAction(PhantasmalKillerPower(amount=self.amount, duration=1, owner=self.owner), self.owner)])
            self.owner.remove_power(self.name)

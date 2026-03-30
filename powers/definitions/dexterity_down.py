"""Dexterity Down power for recurring dexterity loss."""

from actions.combat import ApplyPowerAction
from powers.base import Power, StackType
from powers.definitions.dexterity import DexterityPower
from utils.registry import register


@register("power")
class DexterityDownPower(Power):
    name = "Dexterity Down"
    description = "Lose Dexterity at the end of each turn."
    stack_type = StackType.INTENSITY
    is_buff = False

    def __init__(self, amount: int = 1, duration: int = -1, owner=None):
        super().__init__(amount=amount, duration=duration, owner=owner)

    def on_turn_end(self):
        from engine.runtime_api import add_actions

        if self.owner is not None:
            add_actions([ApplyPowerAction(DexterityPower(amount=-self.amount, owner=self.owner), self.owner)])

"""Constricted power for combat effects."""
from typing import List

from actions.base import Action
from actions.combat import LoseHPAction
from powers.base import Power, StackType
from utils.registry import register


@register("power")
class ConstrictedPower(Power):
    """Lose HP equal to the constricted amount at end of turn."""

    name = "Constricted"
    description = "At the end of your turn, lose HP equal to Constricted."
    stack_type = StackType.INTENSITY
    is_buff = False

    def __init__(self, amount: int = 10, duration: int = -1, owner=None):
        super().__init__(amount=amount, duration=duration, owner=owner)

    def on_turn_end(self) -> List[Action]:
        actions = [LoseHPAction(amount=self.amount, target=self.owner)] if self.amount > 0 else []
        return super().on_turn_end() + actions

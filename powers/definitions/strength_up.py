"""Strength Up power for temporary strength restoration.
Gains Strength at end of turn, then expires.
"""

from typing import List

from localization import LocalStr
from actions.base import Action
from actions.combat import ApplyPowerAction
from powers.base import Power, StackType
from utils.registry import register


@register("power")
class StrengthUpPower(Power):
    """Gain Strength at end of turn and then remove itself."""

    name = "Strength Up"
    description = "At the end of turn, gain {amount} Strength."
    stack_type = StackType.INTENSITY
    is_buff = True
    
    def local(self, field: str, **kwargs) -> LocalStr:
        if field == "description":
            amount = kwargs.get('amount', self.amount)
            return LocalStr(f"{self.localization_key}.description", 
                          default=f"At the end of turn, gain {amount} Strength.",
                          amount=amount)
        return super().local(field)
    def __init__(self, amount: int = 0, duration: int = 1, owner=None):
        super().__init__(amount=amount, duration=duration, owner=owner)

    def on_turn_end(self) -> List[Action]:
        from powers.definitions.strength import StrengthPower
        
        actions: List[Action] = []
        if self.owner and self.amount:
            actions.append(
                ApplyPowerAction(
                    StrengthPower(amount=self.amount, owner=self.owner),
                    self.owner
                )
            )
        self.duration = 0
        return actions

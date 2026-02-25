"""Fading power for combat effects.
Owner dies when countdown reaches zero.
"""

from typing import List

from localization import LocalStr
from actions.base import Action
from powers.base import Power, StackType
from utils.registry import register


@register("power")
class FadingPower(Power):
    """Die when fading countdown expires."""

    name = "Fading"
    description = "Dies in {amount} turns."
    stack_type = StackType.DURATION
    amount_equals_duration = False
    is_buff = False
    
    def local(self, field: str, **kwargs) -> LocalStr:
        if field == "description":
            amount = kwargs.get('amount', self.duration)
            return LocalStr(f"{self.localization_key}.description", 
                          default=f"Dies in {amount} turns.",
                          amount=amount)
        return super().local(field)

    def __init__(self, amount: int = 0, duration: int = 5, owner=None):
        super().__init__(amount=amount, duration=duration, owner=owner)

    def on_turn_end(self) -> List[Action]:
        actions = super().on_turn_end()
        if self.owner and self.duration == 0 and not self.owner.is_dead():
            self.owner.hp = 0
            death_actions = self.owner.on_death()
            if death_actions:
                actions.extend(death_actions)
        return actions

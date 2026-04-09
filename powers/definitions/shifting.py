"""Shifting power for Transient.
Upon losing HP, apply temporary Strength loss and end-of-turn restoration.
"""
from engine.runtime_api import add_action, add_actions

from typing import Any, List

from actions.base import Action
from actions.combat import ApplyPowerAction
from powers.base import Power, StackType
from powers.definitions.strength import StrengthPower
from powers.definitions.strength_up import StrengthUpPower
from utils.registry import register


@register("power")
class ShiftingPower(Power):
    """On damage taken, lose that much Strength until end of turn."""

    name = "Shifting"
    description = "Upon losing HP, loses that much Strength until the end of turn."
    stack_type = StackType.INTENSITY
    is_buff = True

    def __init__(self, owner=None):
        super().__init__(amount=0, duration=-1, owner=owner)

    def on_any_hp_lost(
        self,
        amount: int,
        source: Any = None,
        card: Any = None,
        player: Any = None,
        damage_type: str = "physical",
    ):
        if not self.owner or amount <= 0:
            return
        actions: List[Action] = [
            ApplyPowerAction(
                StrengthPower(amount=-amount, owner=self.owner),
                self.owner
            )
        ]

        strength_up = self.owner.get_power("strength up")
        if strength_up:
            strength_up.amount += amount
            strength_up.duration = 1
        else:
            actions.append(
                ApplyPowerAction(
                    StrengthUpPower(amount=amount, duration=1, owner=self.owner),
                    self.owner
                )
            )

        from engine.game_state import game_state

        add_actions(actions)

        return

"""Defect Biased Cognition power."""

from engine.runtime_api import add_action
from actions.combat import ApplyPowerAction
from powers.base import Power, StackType
from powers.definitions.focus import FocusPower
from utils.registry import register


@register("power")
class BiasedCognitionPower(Power):
    name = "Biased Cognition"
    description = "At the start of each turn, lose 1 Focus."
    stack_type = StackType.PRESENCE
    is_buff = False

    def on_turn_start(self):
        if self.owner is not None:
            add_action(ApplyPowerAction(FocusPower(amount=-1, owner=self.owner), self.owner))

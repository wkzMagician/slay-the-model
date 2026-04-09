"""Defect Self Repair power."""

from engine.runtime_api import add_action
from actions.combat import HealAction
from powers.base import Power, StackType
from utils.registry import register


@register("power")
class SelfRepairPower(Power):
    name = "Self Repair"
    description = "At the end of combat, heal {amount} HP."
    stack_type = StackType.INTENSITY
    is_buff = True

    def on_combat_end(self):
        if self.owner is not None:
            add_action(HealAction(amount=self.amount, target=self.owner))
            self.owner.remove_power(self.name)

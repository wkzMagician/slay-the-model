"""Defect Static Discharge power."""

from engine.runtime_api import add_action
from actions.orb import AddOrbAction
from orbs.lightning import LightningOrb
from powers.base import Power, StackType
from utils.registry import register


@register("power")
class StaticDischargePower(Power):
    name = "Static Discharge"
    description = "Whenever you receive Attack damage, Channel {amount} Lightning."
    stack_type = StackType.INTENSITY
    is_buff = True

    def on_physical_attack_taken(
        self,
        damage: int,
        source=None,
        card=None,
        damage_type: str = "physical",
    ):
        if damage <= 0:
            return
        for _ in range(self.amount):
            add_action(AddOrbAction(LightningOrb()))

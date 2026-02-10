"""
Sentinel power for Ironclad.
When this card is exhausted, gain energy.
"""
from typing import List
from powers.base import Power
from actions.base import Action
from actions.combat import GainEnergyAction
from utils.registry import register


@register("power")
class SentinelPower(Power):
    """When the Sentinel card is exhausted, gain 2/3 energy."""

    name = "Sentinel"
    description = "Gain 2/3 energy when Sentinel is exhausted."
    stackable = False
    amount_equals_duration = False
    is_buff = True

    def __init__(self, amount: int = 2, duration: int = 1, owner=None):
        """
        Args:
            amount: Energy to gain on exhaust (default 2)
            duration: Duration in turns
        """
        super().__init__(amount=amount, duration=duration, owner=owner)

    def on_exhaust(self) -> List[Action]:
        """Gain energy when Sentinel is exhausted."""
        return [GainEnergyAction(energy=self.amount)]

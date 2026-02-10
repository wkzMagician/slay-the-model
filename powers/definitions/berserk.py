"""
Berserk power for Ironclad.
Gain 2 (1) Vulnerable. At start of your turn, gain 1 Energy.
"""
from typing import List, Any
from actions.base import Action
from powers.base import Power
from actions.combat import ApplyPowerAction, GainEnergyAction
from utils.registry import register


@register("power")
class BerserkPower(Power):
    """At start of your turn, gain 1 Energy."""

    name = "Berserk"
    description = "At start of your turn, gain 1 Energy."
    stackable = False
    amount_equals_duration = False
    is_buff = True

    def __init__(self, amount: int = 1, duration: int = 0, owner=None):
        """
        Args:
            amount: Energy to add
            duration: 0 for permanent
        """
        super().__init__(amount=amount, duration=0, owner=owner)

    def on_turn_start(self) -> List[Action]:
        """Gain 1 Energy at start of turn."""
        from engine.game_state import game_state
        from actions.combat import ApplyPowerAction

        actions = []
        if game_state.player:
            actions.append(GainEnergyAction(energy=self.amount))

        return actions

"""
Demon Form power for Ironclad.
At end of your turn, gain Strength.
"""
from typing import List, Any
from powers.base import Power
from actions.base import Action
from utils.registry import register


@register("power")
class DemonFormPower(Power):
    """At start of your turn, gain Strength."""

    name = "Demon Form"
    description = "At end of your turn, gain Strength."
    stackable = True
    amount_equals_duration = False
    is_buff = True

    def __init__(self, amount: int = 2, duration: int = 0, owner=None):
        """
        Args:
            amount: Strength to gain each turn
            duration: 0 for permanent
        """
        super().__init__(amount=amount, duration=-1, owner=owner)

    def on_turn_start(self) -> List[Action]:
        """Gain Strength at end of turn."""
        from actions.combat import ApplyPowerAction
        from engine.game_state import game_state

        actions = []
        if game_state.player:
            actions.append(ApplyPowerAction(
                power="Strength",
                target=game_state.player,
                amount=self.amount
            ))

        return actions

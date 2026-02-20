"""
Shackled power for Dark Shackles card.
At the end of its turn, the enemy gains X Strength.
"""
from typing import List
from actions.base import Action
from actions.combat import ApplyPowerAction
from powers.base import Power
from utils.registry import register


@register("power")
class ShackledPower(Power):
    """Enemy gains Strength at end of its turn."""

    name = "Shackled"
    description = "At the end of its turn, gains Strength."
    stackable = True
    amount_equals_duration = False
    is_buff = False  # This is a buff for the enemy (negative effect)

    def __init__(self, amount: int = 1, owner=None):
        """
        Args:
            amount: Strength to gain (default 1)
        """
        super().__init__(amount=amount, duration=-1, owner=owner)

    def on_turn_end(self) -> List[Action]:
        """Gain Strength at end of turn."""
        from engine.game_state import game_state

        actions = super().on_turn_end()

        if self.owner and self.owner.is_dead():
            return actions

        # Gain Strength
        actions.append(ApplyPowerAction(
            power="Strength",
            target=self.owner,
            amount=self.amount
        ))

        return actions

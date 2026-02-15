"""
Flex power for temporary strength gain.
Gains 2 Strength at the end of your turn.
"""
from typing import Any, List
from actions.base import Action
from powers.base import Power
from utils.registry import register


@register("power")
class FlexPower(Power):
    """Gain 2 Strength at the end of your turn."""
    
    name = "Flex"
    description = "Gain 2 Strength at the end of your turn."
    stackable = True
    is_buff = True
    amount_equals_duration = True  # Duration equals the amount of Strength gained
    
    def __init__(self, amount: int = 2, duration: int = 1, owner=None):
        """
        Args:
            amount: Strength to gain (default 2)
            duration: Turns until power is removed
            owner: Creature with this power
        """
        super().__init__(amount=amount, duration=duration, owner=owner)
    
    def on_turn_end(self) -> List[Action]:
        """Gain Strength at end of turn, then decrease duration."""
        from actions.combat import ApplyPowerAction
        
        actions = []
        
        # Gain Strength
        if self.owner and self.amount > 0:
            actions.append(ApplyPowerAction(
                power="Strength",
                target=self.owner,
                amount=self.amount
            ))
        
        # Decrease duration (handled by base class tick())
        self.tick()
        
        return actions
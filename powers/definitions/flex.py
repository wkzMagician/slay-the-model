"""
Flex power for combat effects.
Gain temporary Strength at start of turn, lose it at end of turn.
"""
from typing import Any, List
from powers.base import Power
from utils.registry import register


@register("power")
class FlexPower(Power):
    """Gain temporary Strength, lose equal amount at end of turn."""
    
    name = "Flex"
    description = "Gain Strength. Lose equal amount at end of turn."
    stackable = False  # Flex doesn't stack, replaces existing
    is_buff = True  # Buff - temporary strength gain
    
    def __init__(self, amount: int = 2, duration: int = 1, owner=None):
        """
        Args:
            amount: Strength to gain (default 2, upgraded 4)
            duration: Duration in turns (default 1)
        """
        super().__init__(amount=amount, duration=duration, owner=owner)
    
    def on_damage_dealt(self, damage: int, target: Any = None,
                      source: Any = None, card: Any = None) -> List:
        """Modify damage dealt based on Flex temporary Strength.
        
        Note: The actual damage modification is handled by the combat system
        checking for this power and reading self.amount.
        """
        # Flex adds temporary Strength that lasts this turn
        # The combat system reads self.amount directly
        return []
    
    def on_player_turn_end(self, player, entities) -> List:
        """Remove Flex power at end of player's turn."""
        # Mark for removal - the combat system will handle actual removal
        self.duration = 0
        return []

"""
Strength power for combat effects.
Increases attack damage by amount.
"""
from typing import Any, List
from powers.base import Power
from utils.registry import register


@register("power")
class StrengthPower(Power):
    """Add Strength that modifies attack damage."""
    
    name = "Strength"
    description = "Increases attack damage by amount."
    stackable = True
    is_buff = True  # Beneficial effect - increases damage
    
    def __init__(self, amount: int = 2, duration: int = 0, owner=None):
        """
        Args:
            amount: Strength to add (default 2, upgraded 4)
            duration: 0 for permanent, positive for temporary turns
        """
        super().__init__(amount=amount, duration=duration, owner=owner)
    
    def on_damage_dealt(self, damage: int, target: Any = None,
                      source: Any = None, card: Any = None) -> List:
        """Modify damage dealt based on Strength.
        
        Note: This method returns a list, but the actual damage modification
        is handled by the combat system reading the strength amount.
        """
        # The actual damage modification is handled by checking strength in combat.py
        # This method is called but returns empty list as damage calculation
        # is done by reading self.amount directly
        return []
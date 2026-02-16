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

    def modify_damage_dealt(self, base_damage: int) -> int:
        """Increase damage dealt by strength amount."""
        return base_damage + self.amount
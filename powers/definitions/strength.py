"""
Strength power for combat effects.
Increases attack damage by amount.
"""
from typing import Any, List
from powers.base import Power, StackType
from utils.registry import register


@register("power")
class StrengthPower(Power):
    """Add Strength that modifies attack damage."""
    
    name = "Strength"
    description = "Increases attack damage by amount."
    stack_type = StackType.INTENSITY
    is_buff = True  # Beneficial effect - increases damage
    is_additive = True  # Additive modifier (applied before multiplicative)
    
    def __init__(self, amount: int = 2, duration: int = -1, owner=None):
        """
        Args:
            amount: Strength to add (default 2, upgraded 4)
            duration: 0 for permanent, positive for temporary turns
        """
        super().__init__(amount=amount, duration=duration, owner=owner)

    @Power.amount.setter
    def amount(self, value: int):
        self._amount = int(value)

    def modify_damage_dealt(self, base_damage: int) -> int:
        """Increase damage dealt by strength amount."""
        return base_damage + self.amount

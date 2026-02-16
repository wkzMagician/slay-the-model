"""
Vulnerable power for combat effects.
Increases damage taken by 50% per stack.
"""
from typing import Any
from powers.base import Power
from utils.registry import register


@register("power")
class VulnerablePower(Power):
    """Increase damage taken by 50% per stack."""
    
    name = "Vulnerable"
    description = "Increases damage taken by 50% per stack."
    stackable = True
    amount_equals_duration = False
    is_buff = False  # Debuff - increases damage taken
    
    def __init__(self, amount: int = 2, duration: int = 2, owner=None):
        """
        Args:
            amount: Vulnerable stacks (default 2)
            duration: Duration in turns (default 2)
        """
        super().__init__(amount=amount, duration=duration, owner=owner)

    def get_damage_taken_multiplier(self) -> float:
        """Return damage multiplier. Vulnerable increases damage taken by 50%."""
        return 1.5
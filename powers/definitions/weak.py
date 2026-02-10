"""
Weak power for combat effects.
Reduces damage dealt by 25%.
"""
from typing import Any, List
from powers.base import Power
from utils.registry import register


@register("power")
class WeakPower(Power):
    """Reduce damage dealt by 25%."""
    
    name = "Weak"
    description = "Reduces damage dealt by 25%."
    stackable = True
    amount_equals_duration = False
    is_buff = False  # Debuff - reduces damage dealt
    
    def __init__(self, amount: int = 2, duration: int = 2, owner=None):
        """
        Args:
            amount: Weak stacks (default 2)
            duration: Duration in turns (default 2)
        """
        super().__init__(amount=amount, duration=duration, owner=owner)
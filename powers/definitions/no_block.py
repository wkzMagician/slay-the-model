"""
No Block power for combat effects.
Prevents gaining block for duration.
"""
from __future__ import annotations
from typing import List
from actions.base import Action
from powers.base import Power, StackType
from utils.registry import register


@register("power")
class NoBlockPower(Power):
    """Cannot gain block for duration."""

    name = "No Block"
    description = "Cannot gain block."
    stack_type = StackType.DURATION
    is_buff = False

    def __init__(self, amount: int = 0, duration: int = 2, owner=None):
        """
        Args:
            amount: Not used (power is binary)
            duration: Duration in turns (default 2)
        """
        super().__init__(amount=amount, duration=duration, owner=owner)
    
    def on_gain_block(self, amount: int, source=None, card=None) -> None:
        """Prevent all block gain."""
        pass

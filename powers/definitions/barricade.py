"""
Barricade power for Ironclad.
Block does not expire at the start of your turn.
"""
from typing import List, Any
from powers.base import Power
from actions.base import Action
from utils.registry import register


@register("power")
class BarricadePower(Power):
    """Block does not expire at the start of your turn."""

    name = "Barricade"
    description = "Block does not expire at the start of your turn."
    stackable = True
    amount_equals_duration = False
    is_buff = True

    def __init__(self, amount: int = 0, duration: int = 0, owner=None):
        """
        Args:
            amount: Not used (set to 0)
            duration: 0 for permanent
        """
        super().__init__(amount=0, duration=0, owner=owner)

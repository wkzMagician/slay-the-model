"""
Barricade power - prevents block from being removed at end of turn.
"""
from typing import Any, List
from actions.base import Action
from powers.base import Power
from utils.registry import register


@register("power")
class BarricadePower(Power):
    """Block does not expire at the end of your turn."""
    
    name = "Barricade"
    description = "Block does not expire at the end of your turn."
    stackable = False
    is_buff = True
    
    def __init__(self, amount: int = 1, duration: int = 0, owner=None):
        super().__init__(amount=amount, duration=duration, owner=owner)
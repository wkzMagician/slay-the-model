"""
Berserk power - gain 2 Strength at start of turn, lose 1 HP.
"""
from typing import Any, List
from actions.base import Action
from powers.base import Power
from utils.registry import register


@register("power")
class BerserkPower(Power):
    """Gain 2 Strength at start of turn. Lose 1 HP."""
    
    name = "Berserk"
    description = "Gain 2 Strength at start of turn. Lose 1 HP."
    stackable = False
    is_buff = True
    
    def __init__(self, amount: int = 1, duration: int = 0, owner=None):
        super().__init__(amount=amount, duration=duration, owner=owner)
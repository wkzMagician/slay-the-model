"""
Buffer Power
Prevents first HP loss in combat (one-time buffer).
"""
from typing import Any, List
from powers.base import Power
from utils.registry import register

@register("power")
class BufferPower(Power):
    """Prevents first HP loss in combat.
    
    Effect: When you would take damage for the first time in combat,
    this relic prevents that damage instead.
    """
    
    name = "Buffer"
    description = "Prevents the next {amount} times you would lose HP."
    stackable = True
    is_buff = True
    
    def __init__(self, amount: int = 0, duration: int = 0, owner=None):
        super().__init__(amount=amount, duration=duration, owner=owner)
    
    def try_prevent_damage(self) -> bool:
        """Attempt to prevent damage. Returns True if damage is prevented.
        
        Decrements the buffer count and returns True if there was a buffer
        charge available.
        """
        if self.amount > 0:
            self.amount -= 1
            return True
        return False

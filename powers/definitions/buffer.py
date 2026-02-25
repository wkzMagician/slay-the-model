"""
Buffer Power
Prevents first HP loss in combat (one-time buffer).
"""
from typing import Any, List

from localization import LocalStr
from powers.base import Power, StackType
from utils.registry import register

@register("power")
class BufferPower(Power):
    """Prevents first HP loss in combat.
    
    Effect: When you would take damage for the first time in combat,
    this relic prevents that damage instead.
    """
    
    name = "Buffer"
    description = "Prevents the next {amount} times you would lose HP."
    stack_type = StackType.INTENSITY
    is_buff = True
    
    def local(self, field: str, **kwargs) -> LocalStr:
        if field == "description":
            amount = kwargs.get('amount', self.amount)
            return LocalStr(f"{self.localization_key}.description", 
                          default=f"Prevents the next {amount} times you would lose HP.",
                          amount=amount)
        return super().local(field)
    def __init__(self, amount: int = 1, duration: int = -1, owner=None):
        # BufferPower is permanent (duration=-1 means infinite)
        # It only expires when amount reaches 0, not based on duration
        # print(f"[DEBUG] BufferPower.__init__ called with amount={amount}, duration={duration}")
        super().__init__(amount=amount, duration=duration, owner=owner)
        # print(f"[DEBUG] After super().__init__: self._duration={self._duration}, self.duration={self.duration}")
    
    def try_prevent_damage(self, amount: int = 0) -> bool:
        """Attempt to prevent damage. Returns True if damage is prevented.
        
        Args:
            amount: The amount of damage to potentially prevent (ignored by Buffer)
        
        Decrements the buffer count and returns True if there was a buffer
        charge available.
        """
        if self.amount > 0:
            self.amount -= 1
            return True
        return False

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
    
    def __init__(self, amount: int = 0, duration: int = 0, owner=None):
        super().__init__(amount=amount, duration=duration, owner=owner)
        self.can_prevent = True  # Can prevent damage once
    
    # TODO: 在DealDamageAction里判断。或者增加 on_attack

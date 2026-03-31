"""Defect Lock-On debuff."""

from powers.base import Power, StackType
from utils.registry import register


@register("power")
class LockOnPower(Power):
    name = "Lock-On"
    description = "Orb effects on this target are increased by 50%."
    stack_type = StackType.DURATION
    is_buff = False

    def __init__(self, amount: int = 0, duration: int = 2, owner=None):
        super().__init__(amount=amount, duration=duration, owner=owner)

    def on_damage_taken(self, damage: int, source=None, card=None, player=None, damage_type: str = "direct"):
        return

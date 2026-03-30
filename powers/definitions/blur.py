"""Blur power for temporary block retention."""

from powers.base import Power, StackType
from utils.registry import register


@register("power")
class BlurPower(Power):
    name = "Blur"
    description = "Block is not removed at the start of your next turn."
    stack_type = StackType.DURATION
    is_buff = True

    def __init__(self, amount: int = 0, duration: int = 1, owner=None):
        super().__init__(amount=amount, duration=duration, owner=owner)

"""Silent power - Accuracy."""

from powers.base import Power, StackType
from utils.registry import register


@register("power")
class AccuracyPower(Power):
    name = "Accuracy"
    description = "Shivs deal additional damage."
    stack_type = StackType.INTENSITY
    is_buff = True

    def __init__(self, amount: int = 4, duration: int = -1, owner=None):
        super().__init__(amount=amount, duration=duration, owner=owner)

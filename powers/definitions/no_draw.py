"""Generic no-draw power used by multiple cards."""

from powers.base import Power, StackType
from utils.registry import register


@register("power")
class NoDrawPower(Power):
    """Cannot draw cards this turn."""

    name = "No Draw"
    description = "Cannot draw cards this turn."
    stack_type = StackType.DURATION
    is_buff = True
    prevents_draw = True

    def __init__(self, amount: int = 0, duration: int = 1, owner=None):
        super().__init__(amount=amount, duration=duration, owner=owner)

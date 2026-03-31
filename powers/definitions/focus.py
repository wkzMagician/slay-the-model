"""Focus Power - Increases orb effectiveness for Defect."""
from powers.base import Power, StackType
from utils.registry import register


@register("power")
class FocusPower(Power):
    name = "Focus"
    description = "Your Orbs gain additional effectiveness equal to {amount}."
    stack_type = StackType.INTENSITY
    is_buff = True

    def __init__(self, amount: int = 0, owner=None, duration: int = -1):
        super().__init__(amount=amount, owner=owner, duration=duration)
        self.is_buff = amount >= 0

    @Power.amount.setter
    def amount(self, value: int):
        self._amount = int(value)
        self.is_buff = self._amount >= 0

"""Defect Electro power."""

from powers.base import Power, StackType
from utils.registry import register


@register("power")
class ElectroPower(Power):
    name = "Electro"
    description = "Your Lightning now hits all enemies."
    stack_type = StackType.PRESENCE
    is_buff = True

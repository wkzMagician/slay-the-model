from powers.base import Power, StackType
from utils.registry import register

@register("power")
class MarkPower(Power):
    name = "Mark"
    description = "When triggered, lose HP equal to Mark."
    stack_type = StackType.INTENSITY
    is_buff = False

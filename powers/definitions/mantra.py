from powers.base import Power, StackType
from utils.registry import register

@register("power")
class MantraPower(Power):
    name = "Mantra"
    description = "When this reaches 10, enter Divinity."
    stack_type = StackType.INTENSITY

from powers.definitions._watcher_common import *

@register("power")
class MarkPower(Power):
    name = "Mark"
    description = "When triggered, lose HP equal to Mark."
    stack_type = StackType.INTENSITY
    is_buff = False

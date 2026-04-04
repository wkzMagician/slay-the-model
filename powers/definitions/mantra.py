from powers.definitions._watcher_common import *

@register("power")
class MantraPower(Power):
    name = "Mantra"
    description = "When this reaches 10, enter Divinity."
    stack_type = StackType.INTENSITY

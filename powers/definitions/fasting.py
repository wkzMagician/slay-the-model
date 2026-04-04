from powers.definitions._watcher_common import *

@register("power")
class FastingPower(Power):
    name = "Fasting"
    description = "Gain 1 less Energy at the start of each turn."
    stack_type = StackType.PRESENCE

    def on_turn_start(self):
        if self.owner is not None:
            self.owner.gain_energy(-1)

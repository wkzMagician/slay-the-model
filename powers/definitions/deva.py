from powers.definitions._watcher_common import *

@register("power")
class DevaPower(Power):
    name = "Deva"
    description = "At the start of your turn, gain Energy, then increase this by 1."
    stack_type = StackType.LINKED
    amount_equals_duration = True

    def on_turn_start(self):
        gain = max(0, self.amount)
        if gain > 0 and self.owner is not None:
            add_action(GainEnergyAction(gain))
        self.amount += 1

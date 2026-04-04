from powers.definitions._watcher_common import *

@register("power")
class CollectPower(Power):
    name = "Collect"
    description = "At the start of your turn, add Miracle+ to your hand."
    stack_type = StackType.DURATION

    def on_turn_start(self):
        from cards.watcher import Miracle

        if self.duration == 0:
            return
        miracle = Miracle()
        miracle.upgrade()
        add_action(AddCardAction(miracle, dest_pile="hand"))
        if self.duration > 0:
            self.duration -= 1
            if self.duration == 0 and self.owner is not None:
                add_action(RemovePowerAction("Collect", self.owner))

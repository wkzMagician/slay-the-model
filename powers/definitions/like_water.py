from powers.definitions._watcher_common import *

@register("power")
class LikeWaterPower(Power):
    name = "Like Water"
    description = "At the end of your turn, if you are in Calm, gain {amount} Block."

    def on_turn_end(self):
        super().on_turn_end()
        if self.owner is None:
            return
        if self.owner.status_manager.status == StatusType.CALM:
            add_action(GainBlockAction(self.amount, target=self.owner))

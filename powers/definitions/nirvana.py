from powers.definitions._watcher_common import *

@register("power")
class NirvanaPower(Power):
    name = "Nirvana"
    description = "Whenever you Scry, gain {amount} Block."

    @subscribe(ScryMessage, priority=MessagePriority.PLAYER_POWER)
    def on_scry(self, count):
        if count > 0 and self.owner is not None:
            add_action(GainBlockAction(self.amount, target=self.owner))

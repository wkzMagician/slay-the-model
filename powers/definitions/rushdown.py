from powers.definitions._watcher_common import *

@register("power")
class RushdownPower(Power):
    name = "Rushdown"
    description = "Whenever you enter Wrath, draw {amount} card(s)."

    @subscribe(StanceChangedMessage, priority=MessagePriority.PLAYER_POWER)
    def on_stance_changed(self, previous_status, new_status):
        if new_status == StatusType.WRATH:
            add_action(DrawCardsAction(self.amount))

from powers.definitions._watcher_common import *

@register("power")
class ForesightPower(Power):
    name = "Foresight"
    description = "At the start of your turn, Scry {amount}."

    def on_turn_start(self):
        from actions.watcher import ScryAction

        add_action(ScryAction(self.amount))

from engine.runtime_api import add_action
from powers.base import Power
from utils.registry import register

@register("power")
class ForesightPower(Power):
    name = "Foresight"
    description = "At the start of your turn, Scry {amount}."

    def on_turn_start(self):
        from actions.watcher import ScryAction

        add_action(ScryAction(self.amount))

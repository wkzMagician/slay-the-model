from engine.runtime_api import add_action
from powers.base import Power
from utils.registry import register

@register("power")
class DevotionPower(Power):
    name = "Devotion"
    description = "At the start of your turn, gain {amount} Mantra."

    def on_turn_start(self):
        from actions.watcher import GainMantraAction

        add_action(GainMantraAction(self.amount))

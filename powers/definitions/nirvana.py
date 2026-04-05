from actions.combat import GainBlockAction
from engine.messages import ScryMessage
from engine.runtime_api import add_action
from engine.subscriptions import MessagePriority, subscribe
from powers.base import Power
from utils.registry import register

@register("power")
class NirvanaPower(Power):
    name = "Nirvana"
    description = "Whenever you Scry, gain {amount} Block."

    @subscribe(ScryMessage, priority=MessagePriority.PLAYER_POWER)
    def on_scry(self, count):
        if count > 0 and self.owner is not None:
            add_action(GainBlockAction(self.amount, target=self.owner))

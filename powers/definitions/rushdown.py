from actions.card import DrawCardsAction
from engine.messages import StanceChangedMessage
from engine.runtime_api import add_action
from engine.subscriptions import MessagePriority, subscribe
from powers.base import Power
from utils.registry import register
from utils.types import StatusType

@register("power")
class RushdownPower(Power):
    name = "Rushdown"
    description = "Whenever you enter Wrath, draw {amount} card(s)."

    @subscribe(StanceChangedMessage, priority=MessagePriority.PLAYER_POWER)
    def on_stance_changed(self, previous_status, new_status):
        if new_status == StatusType.WRATH:
            add_action(DrawCardsAction(self.amount))

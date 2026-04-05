from actions.combat import GainBlockAction
from engine.messages import StanceChangedMessage
from engine.runtime_api import add_action
from engine.subscriptions import MessagePriority, subscribe
from powers.base import Power, StackType
from utils.registry import register

@register("power")
class MentalFortressPower(Power):
    name = "Mental Fortress"
    description = "Whenever you change stances, gain {amount} Block."
    stack_type = StackType.INTENSITY

    @subscribe(StanceChangedMessage, priority=MessagePriority.PLAYER_POWER)
    def on_stance_changed(self, previous_status, new_status):
        if previous_status != new_status and self.owner is not None:
            add_action(GainBlockAction(self.amount, target=self.owner))

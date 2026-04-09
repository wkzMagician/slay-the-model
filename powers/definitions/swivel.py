from engine.messages import CardPlayedMessage
from engine.subscriptions import MessagePriority, subscribe
from powers.base import Power, StackType
from utils.registry import register
from utils.types import CardType


@register("power")
class SwivelPower(Power):
    name = "Swivel"
    description = "Your next Attack this turn costs 0."
    stack_type = StackType.PRESENCE

    def __init__(self, tracked_costs=None, owner=None):
        super().__init__(amount=0, duration=1, owner=owner)
        self.tracked_costs = dict(tracked_costs or {})

    @subscribe(CardPlayedMessage, priority=MessagePriority.PLAYER_POWER)
    def on_card_play(self, card, targets):
        if getattr(card, "card_type", None) != CardType.ATTACK:
            return

        for tracked_card, original_cost in list(self.tracked_costs.items()):
            if tracked_card is card:
                continue
            tracked_card.cost_until_end_of_turn = original_cost

        if self.owner is not None:
            self.owner.remove_power(self.name)

    def on_turn_end(self):
        for tracked_card, original_cost in list(self.tracked_costs.items()):
            tracked_card.cost_until_end_of_turn = original_cost
        if self.owner is not None:
            self.owner.remove_power(self.name)

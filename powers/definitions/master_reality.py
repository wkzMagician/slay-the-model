from engine.messages import CardAddedToPileMessage
from engine.subscriptions import MessagePriority, subscribe
from powers.base import Power, StackType
from utils.registry import register

@register("power")
class MasterRealityPower(Power):
    name = "Master Reality"
    description = "Whenever a card is created during combat, upgrade it."
    stack_type = StackType.PRESENCE

    @subscribe(CardAddedToPileMessage, priority=MessagePriority.PLAYER_POWER)
    def on_card_added(self, card, dest_pile="deck"):
        if card is None or not getattr(card, "can_upgrade", None):
            return
        if dest_pile == "deck":
            return
        if card.can_upgrade():
            card.upgrade()

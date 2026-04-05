from powers.base import Power, StackType
from utils.registry import register

@register("power")
class EstablishmentPower(Power):
    name = "Establishment"
    description = "At the end of your turn, reduce the cost of retained cards by 1."
    stack_type = StackType.PRESENCE

    def on_turn_end(self):
        super().on_turn_end()
        if self.owner is None:
            return
        for card in list(self.owner.card_manager.get_pile("hand")):
            if getattr(card, "retain", False) or getattr(card, "retain_this_turn", False):
                if getattr(card, "_cost", 0) >= 0:
                    card._cost = max(0, card._cost - 1)

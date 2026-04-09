"""Defect Rebound power."""

from powers.base import Power, StackType
from utils.registry import register
from utils.types import CardType


@register("power")
class ReboundPower(Power):
    name = "Rebound"
    description = "The next card you play this turn is put on top of your draw pile."
    stack_type = StackType.PRESENCE
    is_buff = True

    def on_card_play(self, card, targets):
        if self.owner is None:
            return
        if getattr(card, "card_type", None) != CardType.POWER:
            setattr(card, "_rebound_to_draw", True)
        self.owner.remove_power(self.name)

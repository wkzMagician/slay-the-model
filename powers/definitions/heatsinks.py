"""Defect Heatsinks power."""

from engine.runtime_api import add_action
from actions.card import DrawCardsAction
from powers.base import Power, StackType
from utils.registry import register
from utils.types import CardType


@register("power")
class HeatsinksPower(Power):
    name = "Heatsinks"
    description = "Whenever you play a Power card, draw {amount} card(s)."
    stack_type = StackType.INTENSITY
    is_buff = True

    def on_card_play(self, card, targets):
        if getattr(card, "card_type", None) == CardType.POWER:
            add_action(DrawCardsAction(count=self.amount))

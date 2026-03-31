"""Defect Machine Learning power."""

from engine.runtime_api import add_action
from actions.card import DrawCardsAction
from powers.base import Power, StackType
from utils.registry import register


@register("power")
class MachineLearningPower(Power):
    name = "Machine Learning"
    description = "At the start of your turn, draw {amount} additional card(s)."
    stack_type = StackType.INTENSITY
    is_buff = True

    def on_turn_start(self):
        add_action(DrawCardsAction(count=self.amount))

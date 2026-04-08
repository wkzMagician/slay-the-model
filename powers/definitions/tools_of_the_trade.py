"""Tools of the Trade power."""

from actions.card import ChooseDiscardCardAction, DrawCardsAction
from powers.base import Power, StackType
from utils.registry import register


@register("power")
class ToolsOfTheTradePower(Power):
    name = 'Tools of the Trade'
    description = 'At the start of your turn, draw cards and discard cards.'
    stack_type = StackType.INTENSITY
    is_buff = True

    def __init__(self, amount: int = 1, duration: int = -1, owner=None):
        super().__init__(amount=amount, duration=duration, owner=owner)

    def on_turn_start_post_draw(self):
        from engine.runtime_api import add_actions

        add_actions([
            DrawCardsAction(count=self.amount),
            ChooseDiscardCardAction(pile='hand', amount=self.amount),
        ])

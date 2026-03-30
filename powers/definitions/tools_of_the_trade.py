"""Tools of the Trade power."""

from actions.card import ChooseDiscardCardAction, DrawCardsAction
from powers.base import Power, StackType
from utils.registry import register


@register("power")
class ToolsOfTheTradePower(Power):
    name = 'Tools of the Trade'
    description = 'At the start of your turn, draw 1 card and discard 1 card.'
    stack_type = StackType.PRESENCE
    is_buff = True

    def __init__(self, amount: int = 1, duration: int = -1, owner=None):
        super().__init__(amount=amount, duration=duration, owner=owner)

    def on_turn_start(self):
        from engine.runtime_api import add_actions

        add_actions([DrawCardsAction(count=1), ChooseDiscardCardAction(pile='hand', amount=1)])

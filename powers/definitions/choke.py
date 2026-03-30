"""Choke debuff for follow-up damage on card plays."""

from actions.combat import DealDamageAction
from powers.base import Power, StackType
from utils.registry import register


@register("power")
class ChokePower(Power):
    """Whenever the player plays a card this turn, owner takes damage."""

    name = "Choke"
    description = "Whenever you play a card this turn, take damage."
    stack_type = StackType.INTENSITY
    is_buff = False

    def __init__(self, amount: int = 3, duration: int = 1, owner=None):
        super().__init__(amount=amount, duration=duration, owner=owner)

    def on_card_play(self, card, player, targets):
        from engine.runtime_api import add_actions

        add_actions([DealDamageAction(damage=self.amount, target=self.owner, source=player, card=card)])

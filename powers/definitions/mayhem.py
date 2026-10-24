"""
Mayhem power for combat effects.
Play top card of draw pile at start of turn.
"""
from engine.runtime_api import add_action, add_actions
from typing import List
from actions.base import Action
from actions.combat import PlayCardAction
from powers.base import Power, StackType
from utils.registry import register


@register("power")
class MayhemPower(Power):
    """Play top card of draw pile at start of turn."""

    name = "Mayhem"
    description = "Play top card of draw pile at start of turn."
    stack_type = StackType.PRESENCE
    is_buff = True

    def __init__(self, amount: int = 1, duration: int = -1, owner=None):
        """
        Args:
            amount: Not used
            duration: 0 for permanent (this combat)
        """
        super().__init__(amount=amount, duration=duration, owner=owner)

    def on_turn_start(self):
        """Play top card of draw pile at start of turn."""
        from engine.game_state import game_state

        from actions.autoplay import PlayTopCardAction
        from actions.base import LambdaAction
        if game_state.player:
            add_action(LambdaAction(lambda: add_action(PlayTopCardAction(), to_front=True)))
        return

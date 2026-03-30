"""
Rage power for Ironclad.
Whenever you play an ATTACK card this turn, gain block.
"""
from engine.runtime_api import add_action, add_actions
from typing import List, Any
from actions.base import Action
from powers.base import Power, StackType
from actions.combat import GainBlockAction
from utils.registry import register


@register("power")
class RagePower(Power):
    """Whenever you play an ATTACK card this turn, gain 3/5 block."""

    name = "Rage"
    description = "Whenever you play an ATTACK card this turn, gain block."
    stack_type = StackType.INTENSITY
    is_buff = True

    def __init__(self, amount: int = 3, duration: int = 1, owner=None):
        """
        Args:
            amount: Block to gain per attack played (default 3)
            duration: 0 for permanent
        """
        super().__init__(amount=amount, duration=duration, owner=owner)

    def on_play_card(self, card, player, targets):
        """Gain block when an Attack card is played."""
        from engine.game_state import game_state
        from utils.types import CardType

        actions = []

        if game_state.player and hasattr(card, 'card_type'):
            if card.card_type == CardType.ATTACK:
                actions.append(GainBlockAction(block=self.amount, target=game_state.player))

        from engine.game_state import game_state

        add_actions(actions)

        return
"""
Rage power for Ironclad.
Whenever you play an ATTACK card this turn, gain block.
"""
from typing import List, Any
from actions.base import Action
from powers.base import Power
from actions.combat import GainBlockAction
from utils.registry import register


@register("power")
class RagePower(Power):
    """Whenever you play an ATTACK card this turn, gain 3/5 block."""

    name = "Rage"
    description = "Whenever you play an ATTACK card this turn, gain block."
    stackable = True
    amount_equals_duration = False
    is_buff = True

    def __init__(self, amount: int = 3, duration: int = 0, owner=None):
        """
        Args:
            amount: Block to gain per attack played (default 3)
            duration: 0 for permanent
        """
        super().__init__(amount=amount, duration=-1, owner=owner)

    def on_play_card(self, card, player, entities) -> List[Action]:
        """Gain block when an Attack card is played."""
        from engine.game_state import game_state
        from utils.types import CardType

        actions = []

        if game_state.player and hasattr(card, 'card_type'):
            if card.card_type == CardType.ATTACK:
                actions.append(GainBlockAction(block=self.amount, target=game_state.player))

        return actions

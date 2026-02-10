"""
Metallicize power for Ironclad.
Gain block at the end of your turn.
"""
from typing import List, Any
from actions.base import Action
from powers.base import Power
from actions.combat import GainBlockAction
from utils.registry import register


@register("power")
class MetallicizePower(Power):
    """Gain 3/4 block at end of your turn."""

    name = "Metallicize"
    description = "Gain 3/4 block at end of your turn."
    stackable = True
    amount_equals_duration = False
    is_buff = True

    def __init__(self, amount: int = 3, duration: int = 0, owner=None):
        """
        Args:
            amount: Block to gain each turn (default 3)
            duration: 0 for permanent
        """
        super().__init__(amount=amount, duration=0, owner=owner)

    def on_turn_end(self) -> List[Action]:
        """Gain block at end of turn."""
        from engine.game_state import game_state
        actions = []

        if game_state.player:
            actions.append(GainBlockAction(block=self.amount, target=game_state.player))

        return actions

"""
Brutality power for Ironclad.
At start of your turn, lose 1 HP and draw 1 card.
"""
from typing import List
from powers.base import Power
from actions.base import Action
from actions.card import DrawCardsAction
from actions.combat import LoseHPAction
from utils.registry import register


@register("power")
class BrutalityPower(Power):
    """At start of turn, lose HP and draw cards."""

    name = "Brutality"
    description = "At start of your turn, lose 1 HP and draw 1 card."
    stackable = False
    amount_equals_duration = False
    is_buff = True

    def __init__(self, amount: int = 0, duration: int = 0, owner=None):
        """
        Args:
            amount: Not used
            duration: 0 for permanent
        """
        super().__init__(amount=0, duration=-1, owner=owner)

    def on_turn_start(self) -> List[Action]:
        """Lose 1 HP and draw 1 card at turn start."""
        return [
            LoseHPAction(amount=1),
            DrawCardsAction(count=1),
        ]

"""
Painful Stabs power for Corrupt Heart boss.
Adds a Wound to discard pile whenever player plays an Attack.
"""
from engine.runtime_api import add_action, add_actions
from typing import List

from actions.base import Action
from actions.card import AddCardAction
from cards.colorless.wound import Wound
from powers.base import Power, StackType
from utils.registry import register
from utils.types import CardType


@register("power")
class PainfulStabsPower(Power):
    """Whenever the player plays an Attack, add a Wound."""

    name = "Painful Stabs"
    description = "Whenever you play an Attack, shuffle a Wound into discard."
    stack_type = StackType.PRESENCE
    is_buff = True

    def __init__(self, amount: int = 0, duration: int = -1, owner=None):
        """
        Args:
            amount: Not used for this power (non-stackable)
            duration: 0 for permanent (doesn't decay)
        """
        super().__init__(amount=amount, duration=duration, owner=owner)

    def on_card_play(self, card, targets):
        """Add a Wound to discard pile when player plays an Attack."""
        if card is None or getattr(card, "card_type", None) != CardType.ATTACK:
            return
        from engine.game_state import game_state
        add_actions([AddCardAction(card=Wound(), dest_pile="discard_pile")])
        return

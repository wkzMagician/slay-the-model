"""
Double Tap power for Ironclad.
This turn, your next Attack is played twice.
"""
from typing import List, Any
from actions.base import Action
from cards.base import Card
from powers.base import Power, StackType
from utils.registry import register
from utils.types import CardType


@register("power")
class DoubleTapPower(Power):
    """This turn, your next Attack is played twice."""

    name = "Double Tap"
    description = "This turn, your next Attack is played twice."
    stack_type = StackType.INTENSITY
    is_buff = True

    def __init__(self, amount: int = 1, duration: int = 1, owner=None):
        """
        Args:
            amount: Number of attacks to play twice (default 1)
            duration: Duration in turns
        """
        super().__init__(amount=amount, duration=duration, owner=owner)
        
    def on_card_play(self, card: Card, targets):
        if card.card_type == CardType.ATTACK:
            from engine.game_state import game_state

            resolved_targets = getattr(game_state.current_combat.combat_state, "last_card_targets", []) if game_state.current_combat else []
            card.on_play(targets=resolved_targets)
            self.amount -= 1
            if self.owner is not None and self.amount <= 0:
                self.owner.remove_power(self.name)
        return

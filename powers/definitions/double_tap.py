"""
Double Tap power for Ironclad.
This turn, your next Attack is played twice.
"""
from typing import List, Any
from actions.base import Action
from actions.combat import PlayCardAction
from cards.base import Card
from powers.base import Power
from utils.registry import register
from utils.types import CardType


@register("power")
class DoubleTapPower(Power):
    """This turn, your next Attack is played twice."""

    name = "Double Tap"
    description = "This turn, your next Attack is played twice."
    stackable = True
    amount_equals_duration = False
    is_buff = True

    def __init__(self, amount: int = 1, duration: int = 1, owner=None):
        """
        Args:
            amount: Number of attacks to play twice (default 1)
            duration: Duration in turns
        """
        super().__init__(amount=amount, duration=duration, owner=owner)
        
    def on_card_play(self, card: Card, player, entities) -> List[Action]:
        if card.card_type == CardType.ATTACK:
            return card.on_play() * self.amount
        return []

"""
Enrage power - Gains Strength when player plays a Skill card.
"""
from engine.runtime_api import add_action, add_actions
from typing import List, Any
from actions.base import Action
from powers.base import Power, StackType
from actions.combat import ApplyPowerAction
from utils.registry import register


@register("power")
class EnragePower(Power):
    """When the player plays a Skill, gain 1 Strength."""

    name = "Enrage"
    description = "When the player plays a Skill, gain 1 Strength."
    stack_type = StackType.INTENSITY
    is_buff = True

    def __init__(self, amount: int = 1, duration: int = -1, owner=None):
        """
        Args:
            amount: Strength to gain per skill played (default 1)
            duration: -1 for permanent
        """
        super().__init__(amount=amount, duration=duration, owner=owner)

    def on_card_play(self, card, player, targets):
        """Trigger when player plays a card."""
        from utils.types import CardType
        from powers.definitions.strength import StrengthPower
        
        actions = []
        
        # Only trigger when player plays a Skill card
        if hasattr(card, 'card_type') and card.card_type == CardType.SKILL:
            actions.append(
                ApplyPowerAction(
                    StrengthPower(amount=self.amount, duration=self.duration, owner=self.owner),
                    self.owner
                )
            )
        
        from engine.game_state import game_state
        
        add_actions(actions)
        
        return
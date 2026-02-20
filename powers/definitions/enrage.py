"""
Enrage power - Gains Strength when player plays a Skill card.
"""
from typing import List, Any
from actions.base import Action
from powers.base import Power
from actions.combat import ApplyPowerAction
from utils.registry import register


@register("power")
class EnragePower(Power):
    """When the player plays a Skill, gain 1 Strength."""

    name = "Enrage"
    description = "When the player plays a Skill, gain 1 Strength."
    stackable = True
    amount_equals_duration = False
    is_buff = True

    def __init__(self, amount: int = 1, duration: int = 0, owner=None):
        """
        Args:
            amount: Strength to gain per skill played (default 1)
            duration: 0 for permanent
        """
        super().__init__(amount=amount, duration=-1, owner=owner)

    def on_card_play(self, card, player, entities) -> List[Action]:
        """Trigger when player plays a card."""
        from utils.types import CardType
        
        actions = []
        
        # Only trigger when player plays a Skill card
        if hasattr(card, 'card_type') and card.card_type == CardType.SKILL:
            actions.append(
                ApplyPowerAction(
                    power="strength",
                    target=self.owner,
                    amount=self.amount,
                    duration=-1
                )
            )
        
        return actions

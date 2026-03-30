"""
Beat of Death power for Corrupt Heart boss.
Deals damage to player whenever they play a card.
"""
from engine.runtime_api import add_action, add_actions
from typing import List

from actions.base import Action
from actions.combat import DealDamageAction
from powers.base import Power, StackType
from utils.registry import register


@register("power")
class BeatOfDeathPower(Power):
    """Whenever the player plays a card, deal damage to them."""

    name = "Beat of Death"
    description = "Whenever you play a card, take damage."
    stack_type = StackType.INTENSITY
    is_buff = True

    def __init__(self, amount: int = 1, duration: int = -1, owner=None):
        """
        Args:
            amount: Damage dealt per card played
            duration: 0 for permanent (doesn't decay)
        """
        super().__init__(amount=amount, duration=duration, owner=owner)

    def on_card_play(self, card, player, targets):
        """Deal damage to player when they play a card."""
        if player is None or self.owner is None:
            return
        from engine.game_state import game_state
        add_actions(
        [
            DealDamageAction(
                damage=self.amount,
                target=player,
                source=self.owner,
                damage_type="direct",
            )
        ]
        )
        return

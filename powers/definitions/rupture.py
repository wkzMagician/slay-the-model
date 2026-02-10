"""
Rupture power for Ironclad.
Whenever you lose HP from a card, gain Strength.
"""
from typing import List, Any
from actions.base import Action
from powers.base import Power
from actions.combat import ApplyPowerAction
from utils.registry import register


@register("power")
class RupturePower(Power):
    """Whenever you lose HP from a card, gain 1/2 Strength."""

    name = "Rupture"
    description = "Whenever you lose HP from a card, gain Strength."
    stackable = True
    amount_equals_duration = False
    is_buff = True

    def __init__(self, amount: int = 1, duration: int = 0, owner=None):
        """
        Args:
            amount: Strength to gain when HP is lost (default 1)
            duration: 0 for permanent
        """
        super().__init__(amount=amount, duration=0, owner=owner)

    def on_damage_taken(self, damage: int, source: Any = None, card: Any = None,
                       player: Any = None, damage_type: str = "direct") -> List[Action]:
        """Gain Strength when HP is lost from a card."""
        from engine.game_state import game_state

        actions = []

        # Only trigger if damage is from a card
        if damage_type == "hp_loss":
            actions.append(ApplyPowerAction(
                power="Strength",
                target=game_state.player,
                amount=self.amount
            ))

        return actions

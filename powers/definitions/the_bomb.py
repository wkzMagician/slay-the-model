"""
The Bomb power for combat effects.
Deal damage to all enemies after N turns.
"""
from engine.runtime_api import add_action, add_actions
from typing import List
from actions.base import Action
from actions.combat import DealDamageAction
from powers.base import Power, StackType
from utils.registry import register
from utils.types import DamageType


@register("power")
class TheBombPower(Power):
    """Deal damage to all enemies after N turns."""

    name = "The Bomb"
    description = "Deal damage to all enemies after N turns."
    stack_type = StackType.MULTI_INSTANCE
    amount_equals_duration = True  # Duration tracks turns until explosion
    is_buff = True

    def __init__(self, amount: int = 40, duration: int = 3, owner=None):
        """
        Args:
            amount: Damage amount (default 40, upgraded 50)
            duration: Turns until explosion (default 3)
        """
        super().__init__(amount=amount, duration=duration, owner=owner)

    def on_turn_end(self):
        """Deal damage to all enemies when duration reaches 0."""
        super().on_turn_end()
        actions = []
        # Trigger explosion when duration reaches 0 (after tick)
        if self.duration == 0:
            from engine.game_state import game_state
            if game_state.current_combat:
                explosion_actions = []
                for enemy in game_state.current_combat.enemies:
                    explosion_actions.append(DealDamageAction(
                        damage=self.amount,
                        target=enemy,
                        damage_type=DamageType.MAGICAL
                    ))
                return explosion_actions

        from engine.game_state import game_state

        add_actions(actions)

        return

"""
Panache power for combat effects.
Deal damage to all enemies when playing 5 cards.
"""
from engine.runtime_api import add_action, add_actions
from typing import List, Any
from actions.base import Action
from actions.combat import DealDamageAction
from powers.base import Power, StackType
from utils.registry import register


@register("power")
class PanachePower(Power):
    """Deal damage to all enemies when playing 5 cards."""

    name = "Panache"
    description = "Deal damage to all enemies when playing 5 cards."
    stack_type = StackType.INTENSITY
    is_buff = True

    def __init__(self, amount: int = 10, duration: int = -1, owner=None):
        """
        Args:
            amount: Damage amount (default 10, upgraded 14)
            duration: 0 for permanent (this combat)
        """
        super().__init__(amount=amount, duration=duration, owner=owner)

    def on_card_play(self, card, targets):
        """Deal damage to all enemies when playing 5 cards."""
        from engine.game_state import game_state

        # Get cards played this turn (tracked in combat state)
        if game_state.current_combat:
            turn_cards = game_state.current_combat.combat_state.turn_cards_played
            # Trigger every 5 cards (counter resets)
            cards_since_trigger = turn_cards % 5
            if cards_since_trigger == 0 and turn_cards > 0:
                # Deal damage to all enemies
                actions = []
                for enemy in game_state.current_combat.enemies:
                    actions.append(DealDamageAction(
                        damage=self.amount,
                        target=enemy,
                        direct=True
                    ))
                from engine.game_state import game_state
                add_actions(actions)
                return
        return

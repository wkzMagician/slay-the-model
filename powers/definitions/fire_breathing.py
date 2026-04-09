"""
Fire Breathing power for Ironclad.
Whenever you draw a status card, deal damage to ALL enemies.
"""
from engine.runtime_api import add_action, add_actions
from typing import List, Any
from actions.base import Action
from powers.base import Power, StackType
from actions.combat import DealDamageAction
from utils.registry import register
from utils.types import CardType, DamageType


@register("power")
class FireBreathing(Power):
    """Whenever you draw a status card, deal damage to all enemies."""

    name = "Fire Breathing"
    description = "Whenever you draw a status card, deal damage to ALL enemies."
    stack_type = StackType.INTENSITY
    is_buff = True

    def __init__(self, amount: int = 7, duration: int = -1, owner=None):
        """
        Args:
            amount: Damage to deal when status is drawn
            duration: 0 for permanent
        """
        super().__init__(amount=amount, duration=-1, owner=owner)

    def on_card_draw(self, card: Any):
        """Deal damage to all enemies when a status card is drawn."""
        from engine.game_state import game_state
        actions = []

        # Check if drawn card is a status card (non-character card)
        if hasattr(card, 'card_type') and card.card_type == CardType.STATUS:
            if game_state.current_combat:
                enemies = game_state.current_combat.enemies
                for enemy in enemies:
                    if enemy.hp > 0:
                        actions.append(DealDamageAction(
                            damage=self.amount,
                            target=enemy,
                            damage_type=DamageType.MAGICAL,
                            source=self,
                            card=None
                        ))

        from engine.game_state import game_state

        add_actions(actions)

        return

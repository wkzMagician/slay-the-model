"""
Fire Breathing power for Ironclad.
Whenever you draw a status card, deal damage to ALL enemies.
"""
from typing import List, Any
from actions.base import Action
from powers.base import Power
from actions.combat import DealDamageAction
from utils.registry import register
from utils.types import CardType


@register("power")
class FireBreathing(Power):
    """Whenever you draw a status card, deal damage to all enemies."""

    name = "Fire Breathing"
    description = "Whenever you draw a status card, deal damage to ALL enemies."
    stackable = True
    amount_equals_duration = False
    is_buff = True

    def __init__(self, amount: int = 7, duration: int = 0, owner=None):
        """
        Args:
            amount: Damage to deal when status is drawn
            duration: 0 for permanent
        """
        super().__init__(amount=amount, duration=0, owner=owner)

    def on_card_draw(self, card: Any) -> List[Action]:
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
                            damage_type="power",
                            source=self,
                            card=None
                        ))

        return actions

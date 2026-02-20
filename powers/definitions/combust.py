"""
Combust power for Ironclad.
At end of turn, deal damage to all enemies.
"""
from typing import List, Any
from actions.base import Action
from powers.base import Power
from actions.combat import DealDamageAction
from utils.registry import register


@register("power")
class CombustPower(Power):
    """At end of turn, lose 1 heal and deal damage to all enemies."""

    name = "Combust"
    description = "At end of turn, deal damage to all enemies."
    stackable = False
    amount_equals_duration = False
    is_buff = True

    def __init__(self, amount: int = 5, duration: int = 0, owner=None):
        """
        Args:
            amount: Damage to deal each turn
            duration: 0 for permanent
        """
        super().__init__(amount=amount, duration=-1, owner=owner)

    def on_turn_end(self) -> List[Action]:
        """Deal damage to all enemies at end of turn."""
        from engine.game_state import game_state
        player = game_state.player
        actions = []
        
        actions.append(DealDamageAction(damage=1, target=player))

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

        # Call parent method to handle duration tick
        return super().on_turn_end() + actions

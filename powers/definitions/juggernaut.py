"""
Juggernaut power for Ironclad.
Whenever you gain Block, deal damage to all enemies.
"""
from engine.runtime_api import add_action, add_actions
from typing import List, Any
from actions.base import Action
from powers.base import Power, StackType
from actions.combat import DealDamageAction
from utils.combat import resolve_target
from utils.registry import register
from utils.types import DamageType, TargetType


@register("power")
class JuggernautPower(Power):
    """Whenever you gain Block, deal 5/7 damage to ALL enemies."""

    name = "Juggernaut"
    description = "Whenever you gain Block, deal damage to ALL enemies."
    stack_type = StackType.INTENSITY
    is_buff = True

    def __init__(self, amount: int = 5, duration: int = -1, owner=None):
        """
        Args:
            amount: Damage to deal per block gained (default 5)
            duration: 0 for permanent
        """
        super().__init__(amount=amount, duration=-1, owner=owner)

    def on_gain_block(self, amount: int, source: Any = None, card: Any = None):
        """Deal damage to all enemies when block is gained."""
        from engine.game_state import game_state
        actions = []

        if game_state.current_combat:
            enemy = resolve_target(target_type=TargetType.ENEMY_RANDOM)
            if isinstance(enemy, list):
                enemy = enemy[0] if enemy else None
            if enemy is None:
                from engine.game_state import game_state
                add_actions(actions)
                return
            actions.append(DealDamageAction(
                damage=self.amount,
                target=enemy,
                damage_type=DamageType.MAGICAL,
                source=self.owner if self.owner else None,
                card=None
            ))

        from engine.game_state import game_state

        add_actions(actions)

        return

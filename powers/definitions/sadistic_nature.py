"""
Sadistic Nature power for combat effects.
Deal damage when applying debuff to enemy.
"""
from engine.runtime_api import add_action, add_actions
from typing import List
from actions.base import Action
from actions.combat import DealDamageAction
from powers.base import Power, StackType
from utils.registry import register
from utils.types import DamageType


@register("power")
class SadisticNaturePower(Power):
    """Deal damage when applying debuff to enemy."""

    name = "Sadistic Nature"
    description = "Deal damage when applying debuff to enemy."
    stack_type = StackType.INTENSITY
    is_buff = True

    def __init__(self, amount: int = 5, duration: int = -1, owner=None):
        """
        Args:
            amount: Damage amount (default 5, upgraded 7)
            duration: 0 for permanent (this combat)
        """
        super().__init__(amount=amount, duration=duration, owner=owner)

    def on_power_added(self, power, target=None):
        """Deal damage when a debuff is applied to an enemy by the player."""
        from engine.game_state import game_state
        
        actions = []
        
        if self.owner != game_state.player:
            from engine.game_state import game_state
            add_actions(actions)
            return
        if not hasattr(power, 'is_buff') or power.is_buff:
            from engine.game_state import game_state
            add_actions(actions)
            return
        if not hasattr(power, 'owner') or not power.owner:
            from engine.game_state import game_state
            add_actions(actions)
            return
        target = power.owner
        if target == self.owner:
            from engine.game_state import game_state
            add_actions(actions)
            return
        from entities.creature import Creature
        if not isinstance(target, Creature):
            from engine.game_state import game_state
            add_actions(actions)
            return
        if target == game_state.player:
            from engine.game_state import game_state
            add_actions(actions)
            return
        actions.append(DealDamageAction(
            damage=self.amount,
            target=target,
            source=self.owner,
            damage_type=DamageType.MAGICAL
        ))
        
        from engine.game_state import game_state
        
        add_actions(actions)
        
        return

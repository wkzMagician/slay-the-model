"""Cultist specific intentions."""

import random
from typing import List, TYPE_CHECKING

from enemies.intention import Intention

if TYPE_CHECKING:
    from enemies.base import Enemy
    from actions.base import Action


class CultistRitualIntention(Intention):
    """Ritual - Gains 3 Strength."""
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("ritual", enemy)
        # 在__init__中设置基础数值
        self.base_strength_gain = 3
    
    def execute(self) -> List['Action']:
        """Execute Ritual: gains 3 Strength."""
        from actions.combat import ApplyPowerAction
        
        return [
            ApplyPowerAction(
                power="strength",
                target=self.enemy,
                amount=self.base_strength_gain,
                duration=-1  # Permanent
            )
        ]


class CultistAttackIntention(Intention):
    """Attack - Deals 6 damage."""
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("attack", enemy)
        # 在__init__中设置基础数值
        self.base_damage = 6
    
    def execute(self) -> List['Action']:
        """Execute Attack: deals 6 damage to player."""
        from actions.combat import AttackAction
        from engine.game_state import game_state
        
        if not game_state or not game_state.player:
            return []
        
        return [
            AttackAction(
                damage=self.base_damage,
                target=game_state.player,
                source=self.enemy,
                damage_type="attack",
            )
        ]

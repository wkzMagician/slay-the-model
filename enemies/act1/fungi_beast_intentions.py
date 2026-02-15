"""Fungi Beast specific intentions."""

import random
from typing import List, TYPE_CHECKING

from enemies.intention import Intention

if TYPE_CHECKING:
    from enemies.base import Enemy
    from actions.base import Action


class BiteIntention(Intention):
    """Bite - Deals 6 damage."""
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("bite", enemy)
        self.base_damage = 6
    
    def execute(self) -> List['Action']:
        """Execute Bite: deals 6 damage to player."""
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


class GrowIntention(Intention):
    """Grow - Gains 3 Strength (4 on A2+, 5 on A17+)."""
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("grow", enemy)
        # Base: 3 Strength, A2+: 4, A17+: 5
        self.base_strength_gain = 3
    
    def execute(self) -> List['Action']:
        """Execute Grow: gains Strength."""
        from actions.combat import ApplyPowerAction
        
        return [
            ApplyPowerAction(
                power="strength",
                target=self.enemy,
                amount=self.base_strength_gain,
                duration=0  # Permanent
            )
        ]

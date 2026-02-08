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
    
    def execute(self) -> List['Action']:
        """Execute Ritual: gains 3 Strength."""
        from actions.combat import ApplyPowerAction
        
        return [
            ApplyPowerAction(
                power="Strength",
                target=self.enemy,
                amount=3,
                duration=0  # Permanent
            )
        ]


class CultistAttackIntention(Intention):
    """Attack - Deals 6 damage."""
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("attack", enemy)
    
    def execute(self) -> List['Action']:
        """Execute Attack: deals 6 damage to player."""
        from actions.combat import DealDamageAction
        from engine.game_state import game_state
        
        if not game_state or not game_state.player:
            return []
        
        return [
            DealDamageAction(
                name="Cultist Attack",
                damage=6,
                target=game_state.player,
                damage_type="attack",
                source=self.enemy
            )
        ]
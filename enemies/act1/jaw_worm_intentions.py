"""JawWorm specific intentions."""

import random
from typing import List, TYPE_CHECKING

from enemies.intention import Intention

if TYPE_CHECKING:
    from enemies.base import Enemy
    from actions.base import Action
    from engine.game_state import GameState


class ChompIntention(Intention):
    """Chomp - Deals 11 damage."""
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("chomp", enemy)
    
    def execute(self) -> List['Action']:
        """Execute Chomp: deals 11 damage to player."""
        from actions.combat import DealDamageAction
        from engine.game_state import game_state
        
        if not game_state or not game_state.player:
            return []
        
        return [
            DealDamageAction(
                name="Chomp",
                damage=11,
                target=game_state.player,
                damage_type="attack",
                source=self.enemy
            )
        ]


class BellowIntention(Intention):
    """Bellow - Gains 3 Strength and 6 Block."""
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("bellow", enemy)
    
    def execute(self) -> List['Action']:
        """Execute Bellow: gains 3 Strength and 6 Block."""
        from actions.combat import GainBlockAction, ApplyPowerAction
        
        return [
            ApplyPowerAction(
                power="Strength",
                target=self.enemy,
                amount=3,
                duration=0  # Permanent
            ),
            GainBlockAction(
                block=6,
                target=self.enemy
            )
        ]


class ThrashIntention(Intention):
    """Thrash - Deals 7 damage and gains 5 Block."""
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("thrash", enemy)
    
    def execute(self) -> List['Action']:
        """Execute Thrash: deals 7 damage and gains 5 Block."""
        from actions.combat import DealDamageAction, GainBlockAction
        from engine.game_state import game_state
        
        if not game_state or not game_state.player:
            return []
        
        return [
            DealDamageAction(
                name="Thrash",
                damage=7,
                target=game_state.player,
                damage_type="attack",
                source=self.enemy
            ),
            GainBlockAction(
                block=5,
                target=self.enemy
            )
        ]
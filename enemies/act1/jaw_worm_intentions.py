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
        self.base_damage = 11
    
    def execute(self) -> List['Action']:
        """Execute Chomp: deals 11 damage to player."""
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


class BellowIntention(Intention):
    """Bellow - Gains 3 Strength and 6 Block."""
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("bellow", enemy)
        self.base_strength_gain = 3
        self.base_block = 6
    
    def execute(self) -> List['Action']:
        """Execute Bellow: gains 3 Strength and 6 Block."""
        from actions.combat import GainBlockAction, ApplyPowerAction
        
        return [
            ApplyPowerAction(
                power="strength",
                target=self.enemy,
                amount=self.base_strength_gain,
                duration=-1
            ),
            GainBlockAction(
                block=self.base_block,
                target=self.enemy
            )
        ]


class ThrashIntention(Intention):
    """Thrash - Deals 7 damage and gains 5 Block."""
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("thrash", enemy)
        self.base_damage = 7
        self.base_block = 5
    
    def execute(self) -> List['Action']:
        """Execute Thrash: deals 7 damage and gains 5 Block."""
        from actions.combat import AttackAction, GainBlockAction
        from engine.game_state import game_state
        
        if not game_state or not game_state.player:
            return []
        
        base_damage = self.base_damage
        
        return [
            AttackAction(
                damage=lambda: base_damage,
                target=game_state.player,
                source=self.enemy,
                damage_type="attack",
            ),
            GainBlockAction(
                block=self.base_block,
                target=self.enemy
            )
        ]

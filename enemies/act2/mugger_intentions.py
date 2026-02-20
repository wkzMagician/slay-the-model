"""Mugger specific intentions."""

import random
from typing import List, TYPE_CHECKING

from enemies.intention import Intention

if TYPE_CHECKING:
    from enemies.base import Enemy
    from actions.base import Action


class MugIntention(Intention):
    """Mug - Deals 10 damage (11 on A2+)."""
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("mug", enemy)
        self.base_damage = 10
    
    def execute(self) -> List['Action']:
        """Execute Mug: deals damage to player."""
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


class LungeIntention(Intention):
    """Lunge - Deals 16 damage (18 on A2+)."""
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("lunge", enemy)
        self.base_damage = 16
    
    def execute(self) -> List['Action']:
        """Execute Lunge: deals damage to player."""
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


class SmokeBombIntention(Intention):
    """Smoke Bomb - Gains 11 Block (17 on A17+)."""
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("smoke_bomb", enemy)
        self.base_block = 11
    
    def execute(self) -> List['Action']:
        """Execute Smoke Bomb: gains Block."""
        from actions.combat import GainBlockAction
        
        return [
            GainBlockAction(
                block=self.base_block,
                target=self.enemy
            )
        ]


class EscapeIntention(Intention):
    """Escape - Flees combat with player's Gold."""
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("escape", enemy)
    
    def execute(self) -> List['Action']:
        """Execute Escape: flee combat."""
        # TODO: Implement steal gold and escape mechanic
        from actions.combat import RemoveEnemyAction
        return [RemoveEnemyAction(self.enemy)]

"""Centurion specific intentions."""

import random
from typing import List, TYPE_CHECKING

from enemies.intention import Intention

if TYPE_CHECKING:
    from enemies.base import Enemy
    from actions.base import Action


class SlashIntention(Intention):
    """Slash - Deals 12 damage (14 on A3+)."""
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("slash", enemy)
        self.base_damage = 12
    
    def execute(self) -> List['Action']:
        """Execute Slash: deals damage to player."""
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


class ProtectIntention(Intention):
    """Protect - Gives Mystic 15 Block, or self 15 Block if alone (20 on A3+)."""
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("protect", enemy)
        self.base_block = 15
    
    def execute(self) -> List['Action']:
        """Execute Protect: gives Block to Mystic or self."""
        from actions.combat import GainBlockAction
        from engine.game_state import game_state
        
        # Check if Mystic is alive
        if game_state and game_state.combat:
            for enemy in game_state.combat.enemies:
                if enemy.__class__.__name__ == 'Mystic' and enemy.is_alive:
                    return [GainBlockAction(block=self.base_block, target=enemy)]
        
        # If alone or no Mystic, give block to self
        return [GainBlockAction(block=self.base_block, target=self.enemy)]


class FuryIntention(Intention):
    """Fury - Deals 6x3 damage (7x3 on A3+)."""
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("fury", enemy)
        self.base_damage = 6
        self.hits = 3
    
    def execute(self) -> List['Action']:
        """Execute Fury: deals 6x3 damage to player."""
        from actions.combat import AttackAction
        from engine.game_state import game_state
        
        if not game_state or not game_state.player:
            return []
        
        actions = []
        for _ in range(self.hits):
            actions.append(
                AttackAction(
                    damage=self.base_damage,
                    target=game_state.player,
                    source=self.enemy,
                    damage_type="attack",
                )
            )
        return actions

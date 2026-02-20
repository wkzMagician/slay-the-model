"""Snake Plant specific intentions."""

import random
from typing import List, TYPE_CHECKING

from enemies.intention import Intention

if TYPE_CHECKING:
    from enemies.base import Enemy
    from actions.base import Action


class ChompChompIntention(Intention):
    """Chomp Chomp - Deals 7x3 damage (8x3 on A3+)."""
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("chomp_chomp", enemy)
        self.base_damage = 7
        self.hits = 3
    
    def execute(self) -> List['Action']:
        """Execute Chomp Chomp: deals 7x3 damage to player."""
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


class EnfeeblingSporesIntention(Intention):
    """Enfeebling Spores - Applies 2 Frail and 2 Weak."""
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("enfeebling_spores", enemy)
        self.frail_stacks = 2
        self.weak_stacks = 2
    
    def execute(self) -> List['Action']:
        """Execute Enfeebling Spores: applies Frail and Weak."""
        from actions.combat import ApplyPowerAction
        from engine.game_state import game_state
        
        if not game_state or not game_state.player:
            return []
        
        return [
            ApplyPowerAction(
                power="frail",
                target=game_state.player,
                amount=self.frail_stacks,
                duration=1
            ),
            ApplyPowerAction(
                power="weak",
                target=game_state.player,
                amount=self.weak_stacks,
                duration=1
            )
        ]

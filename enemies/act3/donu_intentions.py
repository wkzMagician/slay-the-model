"""Donu Boss intentions for Act 3."""

from typing import List

from actions.combat import (
    AttackAction,
    ApplyPowerAction,
)
from enemies.intention import Intention


class CircleOfPower(Intention):
    """All enemies gain 3 Strength."""
    
    def __init__(self, enemy):
        super().__init__("Circle of Power", enemy)
        self.base_strength_gain = 3
    
    def execute(self) -> List:
        """Execute the intention - give all enemies 3 Strength."""
        from engine.game_state import game_state
        
        actions = []
        # Apply Strength to all enemies
        for enemy in game_state.enemies:
            if not enemy.is_dead:
                actions.append(ApplyPowerAction(
                    power="strength",
                    target=enemy,
                    amount=self.base_strength_gain
                ))
        return actions


class Beam(Intention):
    """Deals 10x2 damage."""
    
    def __init__(self, enemy):
        super().__init__("Beam", enemy)
        self.base_damage = 10
        self.base_hits = 2
    
    def execute(self) -> List:
        """Execute the intention."""
        from engine.game_state import game_state
        
        actions = []
        for _ in range(self.base_hits):
            actions.append(AttackAction(
                damage=self.base_damage,
                target=game_state.player,
                source=self.enemy,
                damage_type="attack"
            ))
        return actions
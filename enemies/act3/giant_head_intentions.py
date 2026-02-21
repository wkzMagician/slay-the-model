"""Giant Head Elite intentions for Act 3."""

import random
from typing import List

from actions.combat import (
    AttackAction,
    ApplyPowerAction,
)
from enemies.intention import Intention


class CountIntention(Intention):
    """Deals 13 damage."""
    
    def __init__(self, enemy):
        super().__init__("Count", enemy)
        self.base_damage = 13
    
    def execute(self) -> List:
        """Execute the intention."""
        from engine.game_state import game_state
        return [AttackAction(
            damage=self.base_damage,
            target=game_state.player,
            source=self.enemy,
            damage_type="attack"
        )]


class GlareIntention(Intention):
    """Applies 1 Weak."""
    
    def __init__(self, enemy):
        super().__init__("Glare", enemy)
        self.base_amount = 1
    
    def execute(self) -> List:
        """Execute the intention."""
        from engine.game_state import game_state
        return [ApplyPowerAction(
            power="weak",
            target=game_state.player,
            amount=self.base_amount,
            duration=1
        )]


class ItIsTimeIntention(Intention):
    """Deals 30+5*N damage (N = times used, max 60). A17+: 40+5*N (max 70)."""
    
    def __init__(self, enemy):
        super().__init__("It Is Time", enemy)
        self.base_damage = 30
        self.base_damage_asc = 40
        self.max_damage = 60
        self.max_damage_asc = 70
    
    def execute(self) -> List:
        """Execute the intention."""
        from engine.game_state import game_state
        # Calculate base damage
        if hasattr(game_state, 'ascension') and game_state.ascension >= 17:
            base = self.base_damage_asc
            max_dmg = self.max_damage_asc
        else:
            base = self.base_damage
            max_dmg = self.max_damage
        
        # Increase damage based on times used
        self.enemy._it_is_time_count += 1
        damage = base + (self.enemy._it_is_time_count - 1) * 5
        damage = min(damage, max_dmg)
        
        return [AttackAction(
            damage=damage,
            target=game_state.player,
            source=self.enemy,
            damage_type="attack"
        )]

"""Shelled Parasite specific intentions."""

import random
from typing import List, TYPE_CHECKING

from enemies.intention import Intention

if TYPE_CHECKING:
    from enemies.base import Enemy
    from actions.base import Action


class DoubleStrikeIntention(Intention):
    """Double Strike - Deals 6x2 damage (7x2 on A3+)."""
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("double_strike", enemy)
        self.base_damage = 6
        self.hits = 2
    
    def execute(self) -> List['Action']:
        """Execute Double Strike: deals 6x2 damage to player."""
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


class LifeSuckIntention(Intention):
    """Life Suck - Deals 10 damage, heals equal to unblocked damage (12 on A3+)."""
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("life_suck", enemy)
        self.base_damage = 10
    
    def execute(self) -> List['Action']:
        """Execute Life Suck: deals damage and heals."""
        from actions.combat import AttackAction, HealAction
        from engine.game_state import game_state
        
        if not game_state or not game_state.player:
            return []
        
        # TODO: Implement proper heal equal to unblocked damage
        return [
            AttackAction(
                damage=self.base_damage,
                target=game_state.player,
                source=self.enemy,
                damage_type="attack",
            ),
            HealAction(
                amount=self.base_damage // 2,  # Approximate
                target=self.enemy
            )
        ]


class FeltIntention(Intention):
    """Felt - Deals 18 damage, applies 2 Frail (21 dmg on A3+)."""
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("felt", enemy)
        self.base_damage = 18
        self.frail_stacks = 2
    
    def execute(self) -> List['Action']:
        """Execute Felt: deals damage and applies Frail."""
        from actions.combat import AttackAction, ApplyPowerAction
        from engine.game_state import game_state
        
        if not game_state or not game_state.player:
            return []
        
        return [
            AttackAction(
                damage=self.base_damage,
                target=game_state.player,
                source=self.enemy,
                damage_type="attack",
            ),
            ApplyPowerAction(
                power="frail",
                target=game_state.player,
                amount=self.frail_stacks,
                duration=1
            )
        ]


class StunnedIntention(Intention):
    """Stunned - Does nothing."""
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("stunned", enemy)
    
    def execute(self) -> List['Action']:
        """Execute Stunned: does nothing."""
        return []

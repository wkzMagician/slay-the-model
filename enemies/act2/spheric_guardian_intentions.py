"""Spheric Guardian specific intentions."""

import random
from typing import List, TYPE_CHECKING

from enemies.intention import Intention

if TYPE_CHECKING:
    from enemies.base import Enemy
    from actions.base import Action


class ActivateIntention(Intention):
    """Activate - Gains 25 Block (35 on A17+)."""
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("activate", enemy)
        self.base_block = 25
    
    def execute(self) -> List['Action']:
        """Execute Activate: gains Block."""
        from actions.combat import GainBlockAction
        
        return [
            GainBlockAction(
                block=self.base_block,
                target=self.enemy
            )
        ]


class DebuffAttackIntention(Intention):
    """Debuff Attack - Deals 10 damage, applies 5 Frail (11 dmg on A3+)."""
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("debuff_attack", enemy)
        self.base_damage = 10
        self.frail_stacks = 5
    
    def execute(self) -> List['Action']:
        """Execute Debuff Attack: deals damage and applies Frail."""
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


class SlamIntention(Intention):
    """Slam - Deals 10x2 damage (11x2 on A3+)."""
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("slam", enemy)
        self.base_damage = 10
        self.hits = 2
    
    def execute(self) -> List['Action']:
        """Execute Slam: deals 10x2 damage to player."""
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


class HardenIntention(Intention):
    """Harden - Deals 10 damage, gains 15 Block (11 dmg on A3+)."""
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("harden", enemy)
        self.base_damage = 10
        self.base_block = 15
    
    def execute(self) -> List['Action']:
        """Execute Harden: deals damage and gains Block."""
        from actions.combat import AttackAction, GainBlockAction
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
            GainBlockAction(
                block=self.base_block,
                target=self.enemy
            )
        ]

"""Reptomancer enemy intentions for Slay the Model."""

import random
from typing import List

from actions.combat import AttackAction, ApplyPowerAction, AddEnemyAction
from enemies.act3.dagger import Dagger
from enemies.intention import Intention
from powers.base import PowerType


class SpawnDaggerIntention(Intention):
    """Reptomancer Spawn Dagger intention - summons a Dagger."""
    
    def __init__(self, enemy):
        super().__init__("Spawn Dagger", enemy)
    
    def execute(self) -> List:
        """Execute Spawn Dagger intention."""
        from engine.game_state import game_state
        
        # Maximum 4 Daggers can be in play
        dagger_count = sum(1 for e in game_state.current_combat.enemies if isinstance(e, Dagger))
        
        if dagger_count < 4:
            return [AddEnemyAction(Dagger())]
        return []


class BigBiteIntention(Intention):
    """Reptomancer Big Bite intention - 30 damage."""
    
    def __init__(self, enemy):
        super().__init__("Big Bite", enemy)
        self.base_damage = 30
    
    def execute(self) -> List:
        """Execute Big Bite intention."""
        from engine.game_state import game_state
        
        return [AttackAction(
            self.enemy.get_damage(self.base_damage),
            game_state.player,
            self.enemy,
            "attack"
        )]


class SnakeStrikeIntention(Intention):
    """Reptomancer Snake Strike intention - 13x2 damage + Weak."""
    
    def __init__(self, enemy):
        super().__init__("Snake Strike", enemy)
        self.base_damage = 13  # A17+ only
        self.base_times = 2
    
    def execute(self) -> List:
        """Execute Snake Strike intention."""
        from engine.game_state import game_state
        
        actions = []
        for _ in range(self.base_times):
            actions.append(AttackAction(
                self.enemy.get_damage(self.base_damage),
                game_state.player,
                self.enemy,
                "attack"
            ))
        actions.append(ApplyPowerAction(PowerType.WEAK, game_state.player, 1, 1))
        return actions

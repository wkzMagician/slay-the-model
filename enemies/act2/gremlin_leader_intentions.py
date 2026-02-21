"""Gremlin Leader intentions - Act 2 Elite enemy."""

import random
from typing import TYPE_CHECKING, List

from actions.combat import AttackAction, GainBlockAction, ApplyPowerAction
from enemies.intention import Intention
from powers.base import PowerType

if TYPE_CHECKING:
    from enemies.act2.gremlin_leader import GremlinLeader


class Encourage(Intention):
    """All enemies gain 3 Strength. Other enemies gain 6 Block."""
    
    def __init__(self, enemy: "GremlinLeader"):
        super().__init__("Encourage", enemy)
        self.base_strength_gain = 3
        self.base_block = 6
    
    def execute(self) -> List:
        """Execute encourage - buff all allies."""
        from engine.game_state import game_state
        enemies = (
            game_state.current_combat.enemies
            if game_state.current_combat is not None
            else []
        )
        
        actions = []
        
        # Apply strength to all enemies (including self)
        for enemy in enemies:
            if enemy.is_alive:
                actions.append(ApplyPowerAction(
                    power=PowerType.STRENGTH,
                    target=enemy,
                    amount=self.base_strength_gain,
                    duration=-1  # Permanent
                ))
                
                # Give block to OTHER enemies (not self)
                if enemy != self.enemy:
                    actions.append(GainBlockAction(
                        block=self.base_block,
                        target=enemy
                    ))
        
        return actions


class Stab(Intention):
    """Deals 6×3 damage."""
    
    def __init__(self, enemy: "GremlinLeader"):
        super().__init__("Stab", enemy)
        self.base_damage = 6
        self._hits = 3
    
    def execute(self) -> List:
        """Execute stab attack."""
        from engine.game_state import game_state
        
        actions = []
        for _ in range(self._hits):
            actions.append(AttackAction(
                damage=self.base_damage,
                target=game_state.player,
                source=self.enemy,
                damage_type="attack"
            ))
        
        return actions


class Rally(Intention):
    """Summon 2 random Gremlins."""
    
    def __init__(self, enemy: "GremlinLeader"):
        super().__init__("Rally!", enemy)
    
    def execute(self) -> List:
        """Execute rally - summon 2 random gremlins."""
        from engine.game_state import game_state
        from actions.combat import AddEnemyAction
        enemies = (
            game_state.current_combat.enemies
            if game_state.current_combat is not None
            else []
        )
        
        # Import gremlin types from act1
        from enemies.act1.gremlin import (
            FatGremlin, SneakyGremlin, MadGremlin,
            ShieldGremlin, GremlinWizard
        )
        
        # Available gremlin types for summoning
        GREMLIN_TYPES = [
            FatGremlin, SneakyGremlin, MadGremlin,
            ShieldGremlin, GremlinWizard
        ]
        
        actions = []
        
        # Check how many gremlins are already present
        gremlin_count = sum(1 for e in enemies
                          if e.is_alive and hasattr(e, '_is_gremlin'))
        
        # Can only have max 3 small gremlins
        to_summon = min(2, 3 - gremlin_count)
        
        for _ in range(to_summon):
            gremlin_class = random.choice(GREMLIN_TYPES)
            actions.append(AddEnemyAction(gremlin_class()))
        
        return actions

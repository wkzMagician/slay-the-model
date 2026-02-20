"""Gremlin Leader - Act 2 Elite enemy."""

import random
from typing import List

from enemies.act2.gremlin_leader_intentions import Encourage, Rally, Stab
from enemies.base import Enemy
from utils.types import EnemyType


class GremlinLeader(Enemy):
    """Elite enemy found in Act 2.
    
    Summons Gremlin minions and buffs them.
    Pattern depends on number of Gremlins in battle.
    Cannot use any intent twice in a row.
    No more than 3 small Gremlins can be present.
    """
    
    enemy_type = EnemyType.ELITE
    
    def __init__(self):
        super().__init__(hp_range=(230, 230))
        
        # Register intentions
        self.add_intention(Encourage(self))
        self.add_intention(Stab(self))
        self.add_intention(Rally(self))
    
    def _count_gremlins(self) -> int:
        """Count alive gremlin minions in battle."""
        from engine.game_state import game_state
        enemies = (
            game_state.current_combat.enemies
            if game_state.current_combat is not None
            else []
        )

        count = 0
        for enemy in enemies:
            if enemy.is_alive and enemy != self:
                # Check if it's a small gremlin (not a Leader or Nob)
                if hasattr(enemy, '_is_gremlin') and enemy._is_gremlin:
                    count += 1
        return count
    
    def determine_next_intention(self, floor: int) -> None:
        """Determine next intention based on gremlin count."""
        # Get last move
        last = self.history_intentions[-1] if self.history_intentions else None
        
        gremlin_count = self._count_gremlins()
        
        # Select move based on gremlin count
        if gremlin_count == 0:
            # With 0 Gremlins: 15% Rally, 85% Stab
            if last == "Rally!":
                # Can't use Rally twice
                self.current_intention = self.intentions["Stab"]
            elif last == "Stab":
                if random.random() < 0.15:
                    self.current_intention = self.intentions["Rally!"]
                else:
                    self.current_intention = self.intentions["Encourage"]
            else:
                if random.random() < 0.15:
                    self.current_intention = self.intentions["Rally!"]
                else:
                    self.current_intention = self.intentions["Stab"]
                    
        elif gremlin_count == 1:
            # With 1 Gremlin: Complex pattern
            if last == "Encourage":
                if random.random() < 0.60:
                    self.current_intention = self.intentions["Rally!"]
                else:
                    self.current_intention = self.intentions["Stab"]
            elif last == "Stab":
                if random.random() < 0.625:
                    self.current_intention = self.intentions["Rally!"]
                else:
                    self.current_intention = self.intentions["Encourage"]
            else:
                # After Rally or first turn
                if random.random() < 0.50:
                    self.current_intention = self.intentions["Stab"]
                else:
                    self.current_intention = self.intentions["Encourage"]
                    
        else:
            # With 2+ Gremlins: 66% Encourage, 34% Stab
            if last == "Encourage":
                self.current_intention = self.intentions["Stab"]
            elif last == "Stab":
                if random.random() < 0.66:
                    self.current_intention = self.intentions["Encourage"]
                else:
                    self.current_intention = self.intentions["Stab"]
            else:
                if random.random() < 0.66:
                    self.current_intention = self.intentions["Encourage"]
                else:
                    self.current_intention = self.intentions["Stab"]

"""Repulsor enemy for Slay the Model."""

import random
from typing import List, Optional

from enemies.act3.repulsor_intentions import DazeIntention, RepulsorAttack
from enemies.base import Enemy
from utils.types import EnemyType


class Repulsor(Enemy):
    """Repulsor is a normal Enemy found exclusively in Act 3.
    
    Special mechanics:
    - Repeatedly gives the player Dazed cards
    - 80% Daze, 20% Attack
    """
    
    enemy_type = EnemyType.NORMAL
    
    def __init__(self):
        super().__init__(hp_range=(40, 45))
        self._turn_count = 0
        self._last_was_attack = False
        
        # Register intentions
        self.add_intention(DazeIntention(self))
        self.add_intention(RepulsorAttack(self))
    
    def determine_next_intention(self, floor: int):
        """Determine next intention based on pattern."""
        self._turn_count += 1
        
        # 80% Daze, 20% Attack
        # Cannot use Attack twice in a row
        
        if self._last_was_attack:
            # Must use Daze
            self._last_was_attack = False
            return self.intentions["Daze"]
        
        if random.random() < 0.2:  # 20% Attack
            self._last_was_attack = True
            return self.intentions["Attack"]
        else:  # 80% Daze
            self._last_was_attack = False
            return self.intentions["Daze"]

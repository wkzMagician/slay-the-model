"""Spiker enemy for Slay the Model."""

import random
from typing import List, Optional

from enemies.act3.spiker_intentions import BuffThorns, SpikeAttack
from enemies.base import Enemy
from utils.types import EnemyType


class Spiker(Enemy):
    """Spiker is a normal Enemy found exclusively in Act 3.
    
    Special mechanics:
    - Focuses on building Thorns to make attacking it dangerous
    - Cannot use Buff Thorns more than 6 times
    """
    
    enemy_type = EnemyType.NORMAL
    
    def __init__(self):
        super().__init__(hp_range=(42, 56)) # todo: 44-60 a7
        self._turn_count = 0
        self._buff_thorns_count = 0
        self._last_was_attack = False
        
        # Register intentions
        self.add_intention(SpikeAttack(self))
        self.add_intention(BuffThorns(self))
    
    def determine_next_intention(self, floor: int):
        """Determine next intention based on pattern."""
        self._turn_count += 1
        
        # 50/50 Attack or Buff Thorns
        # Cannot use Attack twice in a row
        # Cannot use Buff Thorns if used 6 times
        
        if self._buff_thorns_count >= 6:
            # Must use Attack
            self._last_was_attack = True
            return self.intentions["Attack"]
        
        if self._last_was_attack:
            # Can only use Buff Thorns
            self._last_was_attack = False
            self._buff_thorns_count += 1
            return self.intentions["Buff Thorns"]
        
        # 50/50 choice
        if random.random() < 0.5:
            self._last_was_attack = True
            return self.intentions["Attack"]
        else:
            self._last_was_attack = False
            self._buff_thorns_count += 1
            return self.intentions["Buff Thorns"]

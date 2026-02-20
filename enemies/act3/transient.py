"""Transient enemy for Slay the Model."""

from typing import List, Optional

from enemies.act3.transient_intentions import TransientAttack
from enemies.base import Enemy
from utils.types import EnemyType


class Transient(Enemy):
    """Transient is a normal Enemy found exclusively in Act 3.
    
    Special mechanics:
    - Damage scales with turn number: 20 + (turn * 10)
    - Becomes more dangerous the longer the fight goes
    """
    
    enemy_type = EnemyType.NORMAL
    
    def __init__(self):
        super().__init__(hp_range=(100, 100))
        self._turn_count = 0
        
        # Register intentions
        self.add_intention(TransientAttack(self))
    
    def determine_next_intention(self, floor: int) -> Optional[str]:
        """Determine next intention - always Attack."""
        self._turn_count += 1
        return "Attack"

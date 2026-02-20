"""Spire Shield - Act 4 Elite."""

import random
from typing import Optional

from enemies.act4.spire_shield_intentions import Bash, Fortify, Smite
from enemies.base import Enemy
from utils.types import EnemyType


class SpireShield(Enemy):
    """Spire Shield is an Elite found in Act 4.
    
    Pattern: Bash -> Fortify -> Smite -> repeat
    Always starts with Bash.
    """
    
    enemy_type = EnemyType.ELITE
    
    def __init__(self):
        super().__init__(hp_range=(42, 48))
        self.add_intention(Bash(self))
        self.add_intention(Fortify(self))
        self.add_intention(Smite(self))
        
        # Track pattern position
        self._pattern_index = 0
    
    def on_combat_start(self, floor: int):
        """Initialize combat state."""
        super().on_combat_start(floor)
        self._pattern_index = 0
    
    def determine_next_intention(self, floor: int) -> Optional[str]:
        """Follow fixed pattern: Bash -> Fortify -> Smite."""
        pattern = ["Bash", "Fortify", "Smite"]
        intention_name = pattern[self._pattern_index % 3]
        self._pattern_index += 1
        return intention_name

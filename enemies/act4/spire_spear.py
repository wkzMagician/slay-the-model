"""Spire Spear - Act 4 Elite."""

import random
from typing import Optional

from enemies.act4.spire_spear_intentions import Skewer, SearingBurn, Pierce
from enemies.base import Enemy
from utils.types import EnemyType


class SpireSpear(Enemy):
    """Spire Spear is an Elite found in Act 4.
    
    Pattern: Skewer -> Searing Burn -> Pierce -> repeat
    Always starts with Skewer.
    """
    
    enemy_type = EnemyType.ELITE
    
    def __init__(self):
        super().__init__(hp_range=(38, 42))
        self.add_intention(Skewer(self))
        self.add_intention(SearingBurn(self))
        self.add_intention(Pierce(self))
        
        # Track pattern position
        self._pattern_index = 0
    
    def on_combat_start(self, floor: int):
        """Initialize combat state."""
        super().on_combat_start(floor)
        self._pattern_index = 0
    
    def determine_next_intention(self, floor: int) -> Optional[str]:
        """Follow fixed pattern: Skewer -> Searing Burn -> Pierce."""
        pattern = ["Skewer", "Searing Burn", "Pierce"]
        intention_name = pattern[self._pattern_index % 3]
        self._pattern_index += 1
        return intention_name

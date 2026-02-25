"""Spire Growth enemy for Slay the Model."""

import random
from typing import List, Optional

from enemies.act3.spire_growth_intentions import Constrict, QuickTackle, Smash
from enemies.base import Enemy
from utils.types import EnemyType


class SpireGrowth(Enemy):
    """Spire Growth is a normal Enemy found exclusively in Act 3.
    
    Special mechanics:
    - Uses Constrict to apply damage over time
    - Uses Smash if player already has Constricted
    """
    
    enemy_type = EnemyType.NORMAL
    
    def __init__(self):
        super().__init__(hp_range=(170, 170)) # todo: 190 a7
        self._turn_count = 0
        self._last_was_constrict = False
        self._consecutive_quick_tackle = 0
        self._consecutive_smash = 0
        
        # Register intentions
        self.add_intention(Constrict(self))
        self.add_intention(QuickTackle(self))
        self.add_intention(Smash(self))
    
    def determine_next_intention(self, floor: int) -> Optional[str]:
        """Determine next intention based on pattern."""
        self._turn_count += 1
        
        # If Constrict was used last turn or player has Constricted, use Smash
        has_constricted = self._player_has_constricted()
        
        if self._last_was_constrict or has_constricted:
            # Check consecutive constraint
            if self._consecutive_smash < 2:
                self._last_was_constrict = False
                self._consecutive_quick_tackle = 0
                self._consecutive_smash += 1
                return self.intentions["Smash"]
        
        # 50/50 Quick Tackle or Constrict
        if random.random() < 0.5:
            # Check consecutive constraint
            if self._consecutive_quick_tackle < 2:
                self._last_was_constrict = False
                self._consecutive_smash = 0
                self._consecutive_quick_tackle += 1
                return self.intentions["Quick Tackle"]
            else:
                # Must use Constrict
                self._last_was_constrict = True
                self._consecutive_quick_tackle = 0
                self._consecutive_smash = 0
                return self.intentions["Constrict"]
        else:
            self._last_was_constrict = True
            self._consecutive_quick_tackle = 0
            self._consecutive_smash = 0
            return self.intentions["Constrict"]
    
    def _player_has_constricted(self) -> bool:
        """Check if player has Constricted power."""
        from engine.game_state import game_state
        return game_state.player.has_power("constricted")

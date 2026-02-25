"""
Slaver enemies - Blue and Red Slaver.
Human enemies with various attacks.
"""
import random
from typing import List, TYPE_CHECKING
from enemies.base import Enemy
from utils.types import EnemyType
from enemies.act1.slaver_intentions import (
    StabIntention,
    RakeIntention,
    ScrapeIntention,
    EntangleIntention
)

if TYPE_CHECKING:
    from actions.base import Action


class BlueSlaver(Enemy):
    """Blue Slaver - Deals damage and applies Weak."""
    
    enemy_type = EnemyType.NORMAL
    
    def __init__(self):
        super().__init__(
            hp_range=(46, 50) # todo: 48-52 a7
        )
        
        # Register intentions
        self.add_intention(StabIntention(self, damage=12))
        self.add_intention(RakeIntention(self))
    
    def determine_next_intention(self, floor: int = 1):
        """Determine next intention based on history.
        
        Blue Slaver pattern:
        - 60% Stab, 40% Rake
        - Cannot use same attack 3 times in a row
        - On A17: Cannot use Rake twice in a row
        """
        # First turn: random choice
        if not self.history_intentions:
            roll = random.random()
            if roll < 0.60:
                return self.intentions["stab"]
            else:
                return self.intentions["rake"]
        
        # Count consecutive uses
        last = self.history_intentions[-1]
        consecutive_count = 0
        for intention in reversed(self.history_intentions):
            if intention == last:
                consecutive_count += 1
            else:
                break
        
        # Cannot use same attack 3 times in a row
        if consecutive_count >= 2:
            if last == "stab":
                return self.intentions["rake"]
            else:
                return self.intentions["stab"]
        
        # Normal pattern: 60% Stab, 40% Rake
        roll = random.random()
        if roll < 0.60:
            return self.intentions["stab"]
        else:
            return self.intentions["rake"]


class RedSlaver(Enemy):
    """Red Slaver - Deals damage, applies Vulnerable, and can Entangle."""
    
    enemy_type = EnemyType.NORMAL
    
    def __init__(self):
        super().__init__(
            hp_range=(46, 50) # todo: 48-52 a7
        )
        
        # Register intentions
        self.add_intention(StabIntention(self, damage=13))
        self.add_intention(ScrapeIntention(self))
        self.add_intention(EntangleIntention(self))
        
        # Track if Entangle has been used (can only use once per combat)
        self._entangle_used = False
        # Pattern counter for Scrape/Stab before Entangle
        self._pattern_index = 0
    
    def determine_next_intention(self, floor: int = 1):
        """Determine next intention based on history.
        
        Red Slaver pattern:
        - Always starts with Stab
        - Before Entangle: Scrape, Scrape, Stab pattern (25% chance to Entangle each turn)
        - After Entangle: 55% Stab, 45% Scrape
        - Cannot use same attack 3 times in a row
        - Can only use Entangle once per combat
        """
        # First turn: Always Stab
        if not self.history_intentions:
            return self.intentions["stab"]
        
        # If Entangle hasn't been used, 25% chance to use it
        if not self._entangle_used:
            roll = random.random()
            if roll < 0.25:
                self._entangle_used = True
                return self.intentions["entangle"]
        
        # Count consecutive uses
        last = self.history_intentions[-1]
        consecutive_count = 0
        for intention in reversed(self.history_intentions):
            if intention == last:
                consecutive_count += 1
            else:
                break
        
        # Cannot use same attack 3 times in a row
        if consecutive_count >= 2:
            if last == "stab":
                return self.intentions["scrape"]
            else:
                return self.intentions["stab"]
        
        # After Entangle: 55% Stab, 45% Scrape
        # Before Entangle: Scrape, Scrape, Stab pattern
        if self._entangle_used:
            roll = random.random()
            if roll < 0.55:
                return self.intentions["stab"]
            else:
                return self.intentions["scrape"]
        else:
            # Pattern: Scrape, Scrape, Stab
            if self._pattern_index == 0 or self._pattern_index == 1:
                self._pattern_index = (self._pattern_index + 1) % 3
                return self.intentions["scrape"]
            else:
                self._pattern_index = (self._pattern_index + 1) % 3
                return self.intentions["stab"]

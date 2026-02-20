"""Awakened One - Act 3 Boss."""
import random
from typing import Optional

from enemies.act3.awakened_one_intentions import (
    Slash,
    SoulStrike,
    Rebirth,
    DarkEcho,
    Sludge,
    Tackle,
)
from enemies.base import Enemy
from utils.types import EnemyType


class AwakenedOne(Enemy):
    """Awakened One is a Boss found at the end of Act 3.
    
    Phase One:
    - Always starts with Slash
    - Soul Strike (25%), Slash (70%)
    - No Slash 3x in a row, no Soul Strike 2x in a row
    
    Phase Two:
    - Triggered when HP reaches 0
    - Rebirth: Heals to full HP, removes debuffs, loses Curiosity
    - Starts with Dark Echo
    - 50/50 Tackle or Sludge, neither 3x in a row
    """
    
    enemy_type = EnemyType.BOSS
    
    def __init__(self):
        super().__init__(hp_range=(300, 300))
        self.add_intention(Slash(self))
        self.add_intention(SoulStrike(self))
        self.add_intention(Rebirth(self))
        self.add_intention(DarkEcho(self))
        self.add_intention(Sludge(self))
        self.add_intention(Tackle(self))
        
        self._phase = 1
    
    def on_combat_start(self, floor: int):
        """Initialize combat state."""
        super().on_combat_start(floor)
        self._phase = 1
    
    def on_damage_taken(self):
        """Check for phase transition."""
        super().on_damage_taken()
        # Trigger rebirth when HP reaches 0 in phase 1
        if self._phase == 1 and self.hp <= 0:
            self.hp = 0  # Keep at 0, rebirth will heal
            self.current_intention = self.intentions["Rebirth"]
    
    def determine_next_intention(self, floor: int) -> Optional[str]:
        """Determine the next intention based on AI pattern."""
        # If rebirth is queued, use it
        if self.current_intention and self.current_intention.name == "Rebirth":
            return "Rebirth"
        
        # Phase 1 pattern
        if self._phase == 1:
            # First turn: always Slash
            if not self.history_intentions:
                return "Slash"
            
            # Count consecutive uses
            slash_count = 0
            soul_strike_count = 0
            
            for move in reversed(self.history_intentions):
                if move == "Slash":
                    slash_count += 1
                elif move == "Soul Strike":
                    soul_strike_count += 1
                else:
                    break
            
            # 70% Slash, 25% Soul Strike
            while True:
                roll = random.random()
                if roll < 0.70:  # 70% Slash
                    if slash_count < 2:  # Not 3x in a row
                        return "Slash"
                else:  # 25% Soul Strike
                    if soul_strike_count < 1:  # Not 2x in a row
                        return "Soul Strike"
        
        # Phase 2 pattern
        else:
            # First turn of phase 2: always Dark Echo
            if not self.history_intentions or self.history_intentions[-1] == "Rebirth":
                return "Dark Echo"
            
            # Count consecutive uses
            tackle_count = 0
            sludge_count = 0
            
            for move in reversed(self.history_intentions):
                if move == "Tackle":
                    tackle_count += 1
                elif move == "Sludge":
                    sludge_count += 1
                else:
                    break
            
            # 50/50 Tackle or Sludge
            while True:
                roll = random.random()
                if roll < 0.50:  # 50% Tackle
                    if tackle_count < 2:  # Not 3x in a row
                        return "Tackle"
                else:  # 50% Sludge
                    if sludge_count < 2:  # Not 3x in a row
                        return "Sludge"
        
        return "Slash"  # Fallback

"""The Champ - Act 2 Elite enemy."""

import random
from typing import List

from enemies.act2.the_champ_intentions import (
    Anger, DefensiveStance, Escalate, FaceSlap, Glint, HeavySlash, Taunt
)
from enemies.base import Enemy
from utils.types import EnemyType


class TheChamp(Enemy):
    """Elite enemy found in Act 2.
    
    Two-phase boss-like elite.
    Phase 1 (HP > 50%): Heavy Slash every 4 turns, 
                        Face Slap/Defensive Stance alternating.
    Phase 2 (HP <= 50%): Uses Anger on first turn, then 
                         repeats random move + Escalate pattern.
    """
    
    enemy_type = EnemyType.ELITE
    
    def __init__(self):
        super().__init__(hp_range=(200, 200))
        self._turn_count = 0
        self._phase = 1
        self._in_phase_two = False
        
        # Register intentions
        self.add_intention(HeavySlash(self))
        self.add_intention(FaceSlap(self))
        self.add_intention(DefensiveStance(self))
        self.add_intention(Glint(self))
        self.add_intention(Taunt(self))
        self.add_intention(Anger(self))
        self.add_intention(Escalate(self))
    
    def on_combat_start(self, floor: int) -> None:
        """Initialize combat state."""
        super().on_combat_start(floor)
        self._turn_count = 0
        self._phase = 1
        self._in_phase_two = False
    
    def on_damage_taken(self, damage: int) -> None:
        """Check for phase transition."""
        if self.hp <= self.max_hp // 2 and self._phase == 1:
            self._phase = 2
    
    def determine_next_intention(self, floor: int) -> None:
        """Determine next intention based on phase."""
        self._turn_count += 1
        
        # Check for phase transition
        if self.hp <= self.max_hp // 2 and self._phase == 1:
            self._phase = 2
        
        # Get last move
        last = self.history_intentions[-1] if self.history_intentions else None
        
        if self._phase == 1:
            self._determine_phase_one_intention(last)
        else:
            self._determine_phase_two_intention(last)
    
    def _determine_phase_one_intention(self, last: str) -> None:
        """Determine intention in Phase One."""
        # Heavy Slash every 4 turns
        if self._turn_count % 4 == 0:
            self.current_intention = self.intentions["Heavy Slash"]
            return
        
        # 50/50 Face Slap or Defensive Stance, but not same twice
        if last == "Face Slap":
            self.current_intention = self.intentions["Defensive Stance"]
        elif last == "Defensive Stance":
            self.current_intention = self.intentions["Face Slap"]
        else:
            if random.random() < 0.50:
                self.current_intention = self.intentions["Face Slap"]
            else:
                self.current_intention = self.intentions["Defensive Stance"]
    
    def _determine_phase_two_intention(self, last: str) -> None:
        """Determine intention in Phase Two."""
        # First turn of Phase Two: Anger
        if not self._in_phase_two:
            self._in_phase_two = True
            self.current_intention = self.intentions["Anger"]
            return
        
        # After first turn: random move (Phase 1 pattern) then Escalate
        # This is a simplified version - in the real game it's more complex
        if last == "Escalate":
            # Choose random move from Phase 1 pattern
            if last == "Face Slap" or (last != "Defensive Stance" and random.random() < 0.50):
                self.current_intention = self.intentions["Face Slap"]
            else:
                self.current_intention = self.intentions["Defensive Stance"]
        else:
            # After random move, use Escalate
            self.current_intention = self.intentions["Escalate"]

"""The Champ - Act 2 Boss enemy."""

import random
from typing import List

from enemies.act2.the_champ_intentions import (
    Anger, DefensiveStance, Execute, FaceSlap, Gloat, HeavySlash, Taunt
)
from enemies.base import Enemy
from utils.types import EnemyType


class TheChamp(Enemy):
    """Boss enemy found at the end of Act 2.
    
    Two-phase boss:
    Phase 1 (HP > 50%): Uses Taunt every 4 turns, 
                        random moves on other turns.
    Phase 2 (HP <= 50%): Uses Anger, then Execute,
                         then pattern: Random, Random, Execute.
    
    Ascension modifiers:
    - A4+: Higher damage on Heavy Slash and Face Slap
    - A9+: Higher HP (320)
    - A19: Gloat replaced with Defensive Stance (with exception)
    """
    
    enemy_type = EnemyType.BOSS
    
    def __init__(self, ascension: int = 0):
        """Initialize The Champ.
        
        Args:
            ascension: Current ascension level
        """
        # HP: 300 (320 on A9+)
        if ascension >= 9:
            hp_max = 320
        else:
            hp_max = 300
        super().__init__(hp_range=(hp_max, hp_max))
        
        self._ascension = ascension
        self._turn_count = 0
        self._phase = 1
        self._phase_two_turn = 0  # Turn counter within phase 2
        self._anger_used = False
        self._execute_after_anger = False
        
        # Register intentions
        self._register_intentions()
    
    def _register_intentions(self) -> None:
        """Register and configure all intentions."""
        heavy_slash = HeavySlash(self)
        face_slap = FaceSlap(self)
        defensive_stance = DefensiveStance(self)
        gloat = Gloat(self)
        taunt = Taunt(self)
        anger = Anger(self)
        execute = Execute(self)
        
        # Apply ascension modifiers
        if self._ascension >= 4:
            heavy_slash.base_damage = 18
            face_slap.base_damage = 14
            gloat.base_strength_gain = 3
            anger.base_strength_gain = 9
        
        if self._ascension >= 9:
            defensive_stance.base_block = 18
            defensive_stance.base_metallicize = 6
        
        if self._ascension >= 19:
            defensive_stance.base_block = 20
            defensive_stance.base_metallicize = 7
            gloat.base_strength_gain = 4
            anger.base_strength_gain = 12
        
        self.add_intention(heavy_slash)
        self.add_intention(face_slap)
        self.add_intention(defensive_stance)
        self.add_intention(gloat)
        self.add_intention(taunt)
        self.add_intention(anger)
        self.add_intention(execute)
    
    def on_combat_start(self, floor: int) -> None:
        """Initialize combat state."""
        super().on_combat_start(floor)
        self._turn_count = 0
        self._phase = 1
        self._phase_two_turn = 0
        self._anger_used = False
        self._execute_after_anger = False
    
    def on_damage_taken(self, damage: int) -> None:
        """Check for phase transition."""
        if self.hp <= self.max_hp // 2 and self._phase == 1:
            # Will trigger phase 2 on next intention determination
            pass
    
    def determine_next_intention(self, floor: int) -> None:
        """Determine next intention based on phase."""
        self._turn_count += 1
        
        # Check for phase transition (HP drops below 50%)
        if self.hp <= self.max_hp // 2 and self._phase == 1:
            self._phase = 2
            self._phase_two_turn = 0
            self._anger_used = False
            self._execute_after_anger = False
        
        if self._phase == 1:
            self._determine_phase_one_intention()
        else:
            self._determine_phase_two_intention()
    
    def _get_last_move(self) -> str:
        """Get the name of the last used intention."""
        if self.history_intentions:
            return self.history_intentions[-1]
        return ""
    
    def _determine_phase_one_intention(self) -> None:
        """Determine intention in Phase One.
        
        Pattern:
        - Always uses Taunt every 4 turns
        - On other turns:
          - Defensive Stance: 15%
          - Gloat: 15% (replaced with Defensive Stance on A19)
          - Face Slap: 25%
          - Heavy Slash: 45%
        - No move can be used twice in a row
        - On A19, if last move was Defensive Stance and Gloat would be
          replaced, use Gloat instead
        """
        last_move = self._get_last_move()
        
        # Taunt every 4 turns
        if self._turn_count % 4 == 0:
            self.current_intention = self.intentions["Taunt"]
            return
        
        # Available moves with probabilities
        moves = [
            ("Defensive Stance", 15),
            ("Gloat", 15),
            ("Face Slap", 25),
            ("Heavy Slash", 45),
        ]
        
        # A19: Gloat replaced with Defensive Stance
        if self._ascension >= 19:
            moves = [
                ("Defensive Stance", 30),  # 15 + 15 from Gloat
                ("Face Slap", 25),
                ("Heavy Slash", 45),
            ]
        
        # Filter out last move (no repeat)
        available = [(name, prob) for name, prob in moves if name != last_move]
        
        # A19 special case: if last move was Defensive Stance, use Gloat
        if self._ascension >= 19 and last_move == "Defensive Stance":
            self.current_intention = self.intentions["Gloat"]
            return
        
        # Select random move based on weights
        if available:
            total_weight = sum(prob for _, prob in available)
            roll = random.randint(1, total_weight)
            cumulative = 0
            for name, prob in available:
                cumulative += prob
                if roll <= cumulative:
                    self.current_intention = self.intentions[name]
                    return
        
        # Fallback
        self.current_intention = self.intentions["Heavy Slash"]
    
    def _determine_phase_two_intention(self) -> None:
        """Determine intention in Phase Two.
        
        Pattern:
        1. First turn: Anger
        2. Turn after Anger: Execute
        3. Then repeat: Random, Random, Execute
        """
        self._phase_two_turn += 1
        
        # First turn of Phase Two: Anger
        if not self._anger_used:
            self.current_intention = self.intentions["Anger"]
            self._anger_used = True
            return
        
        # Turn after Anger: Execute
        if self._phase_two_turn == 2:
            self.current_intention = self.intentions["Execute"]
            return
        
        # Pattern: Random, Random, Execute (repeating)
        # _phase_two_turn starts at 1 (Anger), 2 (Execute)
        # So pattern starts at turn 3
        pattern_turn = (self._phase_two_turn - 3) % 3  # 0, 1, 2, 0, 1, 2...
        
        if pattern_turn == 2:
            # Execute turn
            self.current_intention = self.intentions["Execute"]
        else:
            # Random move (same chances as Phase One)
            self._determine_phase_one_intention()
"""Awakened One - Act 3 Boss."""
import random
from typing import List, Optional

from enemies.act3.awakened_one_intentions import (
    Slash,
    SoulStrike,
    Rebirth,
    DarkEcho,
    Sludge,
    Tackle,
)
from enemies.base import Enemy
from powers.definitions.regeneration import RegenerationPower
from powers.definitions.curiosity import CuriosityPower
from powers.definitions.strength import StrengthPower
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
        super().__init__(hp_range=(300, 300)) # todo: 320 a9
        self.add_intention(Slash(self))
        self.add_intention(SoulStrike(self))
        self.add_intention(Rebirth(self))
        self.add_intention(DarkEcho(self))
        self.add_intention(Sludge(self))
        self.add_intention(Tackle(self))
        
        self._phase = 1
    
    def on_combat_start(self, floor: int):
        """Initialize combat state with starting powers.
        
        Phase 1 starting powers:
        - Regeneration: 10 (15 on Ascension 19+)
        - Curiosity: 1 (2 on Ascension 19+)
        - Strength: 2 on Ascension 4+
        """
        super().on_combat_start(floor)
        self._phase = 1
        
        # Get ascension level from game state
        from engine.game_state import game_state
        ascension = game_state.ascension
        
        # Regeneration: 10 normally, 15 on A19+
        # Note: RegenerationPower uses duration to determine heal amount
        # (amount_equals_duration=True), so we pass regen_amount as duration
        regen_amount = 15 if ascension >= 19 else 10
        self.add_power(RegenerationPower(duration=regen_amount, owner=self))
        
        # Curiosity: 1 normally, 2 on A19+
        curiosity_amount = 2 if ascension >= 19 else 1
        self.add_power(CuriosityPower(amount=curiosity_amount, owner=self))
        
        # Strength: 2 on A4+
        if ascension >= 4:
            self.add_power(StrengthPower(amount=2, owner=self))
    
    def is_dead(self) -> bool:
        """Only dead when HP <= 0 in phase 2.
        
        In phase 1, reaching 0 HP triggers rebirth instead of death.
        """
        return self._phase == 2 and self.hp <= 0

    def on_damage_taken(self, damage: int, source=None, card=None,
                        damage_type=None) -> List['Action']:
        """Check for phase transition."""
        # Trigger rebirth when HP reaches 0 in phase 1
        if self._phase == 1 and self.hp <= 0:
            self.hp = 0  # Keep at 0, rebirth will heal
            self.current_intention = self.intentions["Rebirth"]
        return super().on_damage_taken(damage, source, card, damage_type)
    
    def determine_next_intention(self, floor: int) -> Optional[str]:
        """Determine the next intention based on AI pattern."""
        # If rebirth is queued, use it
        if self.current_intention and self.current_intention.name == "Rebirth":
            return self.intentions["Rebirth"]
        
        # Phase 1 pattern
        if self._phase == 1:
            # First turn: always Slash
            if not self.history_intentions:
                return self.intentions["Slash"]
            
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
                        return self.intentions["Slash"]
                else:  # 25% Soul Strike
                    if soul_strike_count < 1:  # Not 2x in a row
                        return self.intentions["Soul Strike"]
        
        # Phase 2 pattern
        else:
            # First turn of phase 2: always Dark Echo
            if not self.history_intentions or self.history_intentions[-1] == "Rebirth":
                return self.intentions["Dark Echo"]
            
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
                        return self.intentions["Tackle"]
                else:  # 50% Sludge
                    if sludge_count < 2:  # Not 3x in a row
                        return self.intentions["Sludge"]

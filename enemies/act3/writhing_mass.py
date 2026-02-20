"""Writhing Mass enemy for Slay the Model."""

import random
from typing import List, Optional

from enemies.act3.writhing_mass_intentions import (
    MultiHit, DebuffAttackMass, BigHit, BlockAttackMass, ParasiteIntention
)
from enemies.base import Enemy
from utils.types import EnemyType


class WrithingMass(Enemy):
    """Writhing Mass is a normal Enemy found in Act 3.
    
    Special mechanics:
    - First turn: equal chance of Multi Hit, Big Hit, or Debuff Attack
    - After: Parasite 10%, Block Attack 30%, Debuff Attack 30%, Big Hit 30%
    - Cannot use same move twice in a row
    """
    
    enemy_type = EnemyType.NORMAL
    
    def __init__(self):
        super().__init__(hp_range=(130, 130))
        self._turn_count = 0
        self._last_intention = None
        
        # Register intentions
        self.add_intention(MultiHit(self))
        self.add_intention(DebuffAttackMass(self))
        self.add_intention(BigHit(self))
        self.add_intention(BlockAttackMass(self))
        self.add_intention(ParasiteIntention(self))
    
    def determine_next_intention(self, floor: int) -> Optional[str]:
        """Determine next intention based on pattern."""
        self._turn_count += 1
        
        if self._turn_count == 1:
            # First turn: equal chance of Multi Hit, Big Hit, or Debuff Attack
            choice = random.choice(["Multi Hit", "Big Hit", "Debuff Attack"])
            self._last_intention = choice
            return choice
        
        # After first turn:
        # Parasite 10%, Block Attack 30%, Debuff Attack 30%, Big Hit 30%
        roll = random.random()
        
        if roll < 0.1:  # 10% Parasite
            if self._last_intention != "Parasite":
                self._last_intention = "Parasite"
                return "Parasite"
        elif roll < 0.4:  # 30% Block Attack
            if self._last_intention != "Block Attack":
                self._last_intention = "Block Attack"
                return "Block Attack"
        elif roll < 0.7:  # 30% Debuff Attack
            if self._last_intention != "Debuff Attack":
                self._last_intention = "Debuff Attack"
                return "Debuff Attack"
        else:  # 30% Big Hit
            if self._last_intention != "Big Hit":
                self._last_intention = "Big Hit"
                return "Big Hit"
        
        # If we hit a repeat, try again with a different option
        available = ["Multi Hit", "Debuff Attack", "Big Hit", "Block Attack"]
        if self._last_intention in available:
            available.remove(self._last_intention)
        choice = random.choice(available)
        self._last_intention = choice
        return choice

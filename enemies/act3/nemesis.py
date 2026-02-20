"""Nemesis elite enemy - Act 3 Elite."""

import random
from typing import Optional

from enemies.act3.nemesis_intentions import (
    TriAttack,
    TriBurn,
    Scythe,
)
from enemies.base import Enemy
from utils.types import EnemyType


class Nemesis(Enemy):
    """Nemesis is an Elite enemy found exclusively in Act 3.
    
    Pattern:
    - First turn: 50% Tri Attack or 50% Tri Burn
    - Afterwards:
      - Tri Burn (10% chance)
      - Tri Attack (30% chance)
      - Scythe (60% chance)
    - Cannot use Tri Burn or Scythe twice in a row
    - Cannot use Tri Attack three times in a row
    """
    
    enemy_type = EnemyType.ELITE
    
    def __init__(self):
        super().__init__(hp_range=(180, 180))
        self.add_intention(TriAttack(self))
        self.add_intention(TriBurn(self))
        self.add_intention(Scythe(self))
        self._turn_count = 0
    
    def on_combat_start(self, floor: int):
        """Reset state on combat start."""
        super().on_combat_start(floor)
        self._turn_count = 0
    
    def determine_next_intention(self, floor: int):
        """Determine next intention based on Nemesis pattern."""
        self._turn_count += 1
        
        # First turn: 50% Tri Attack or 50% Tri Burn
        if self._turn_count == 1:
            if random.random() < 0.5:
                self.current_intention = self.intentions["Tri Attack"]
            else:
                self.current_intention = self.intentions["Tri Burn"]
            return
        
        # Get last move
        last_move = self.history_intentions[-1] if self.history_intentions else None
        
        # Check consecutive uses
        tri_attack_count = 0
        for intent in reversed(self.history_intentions):
            if intent == "Tri Attack":
                tri_attack_count += 1
            else:
                break
        
        # Build valid options list
        valid_options = []
        
        # Tri Attack: Cannot use 3 times in a row
        if tri_attack_count < 2:
            # 30% chance for Tri Attack
            valid_options.extend(["Tri Attack"] * 30)
        
        # Tri Burn: Cannot use twice in a row
        if last_move != "Tri Burn":
            # 10% chance for Tri Burn
            valid_options.extend(["Tri Burn"] * 10)
        
        # Scythe: Cannot use twice in a row
        if last_move != "Scythe":
            # 60% chance for Scythe
            valid_options.extend(["Scythe"] * 60)
        
        # Random selection
        if valid_options:
            choice = random.choice(valid_options)
            self.current_intention = self.intentions[choice]
        else:
            # Fallback to Tri Attack if nothing valid
            self.current_intention = self.intentions["Tri Attack"]

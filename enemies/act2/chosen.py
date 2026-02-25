"""
Chosen - Normal enemy (Act 2)
Cultist with hex and drain abilities.
"""
import random
from enemies.base import Enemy
from utils.types import EnemyType
from enemies.act2.chosen_intentions import (
    PokeIntention, HexIntention, DebilitateIntention, DrainIntention, ZapIntention
)


class Chosen(Enemy):
    """Chosen - Cultist enemy with hex and drain abilities."""
    
    enemy_type = EnemyType.NORMAL
    
    def __init__(self):
        super().__init__(
            hp_range=(95, 99) # todo: 98-103 a7
        )
        
        # Track pattern phase
        self._turn_count = 0
        
        # Register intentions
        self.add_intention(PokeIntention(self))
        self.add_intention(HexIntention(self))
        self.add_intention(DebilitateIntention(self))
        self.add_intention(DrainIntention(self))
        self.add_intention(ZapIntention(self))
    
    def on_combat_start(self, floor: int = 1):
        """Initialize combat state."""
        super().on_combat_start(floor)
        self._turn_count = 0
    
    def determine_next_intention(self, floor: int = 1):
        """Determine next intention based on pattern."""
        self._turn_count += 1
        
        # Always starts with Poke followed by Hex
        if self._turn_count == 1:
            return self.intentions["poke"]
        
        if self._turn_count == 2:
            return self.intentions["hex"]
        
        # After that, repeat pattern:
        # 1. Debilitate (50%) or Drain (50%)
        # 2. Poke (60%) or Zap (40%)
        
        # Determine which step of the repeating pattern we're on
        pattern_step = (self._turn_count - 3) % 2
        
        if pattern_step == 0:
            # Step 1: Debilitate or Drain
            if random.random() < 0.50:
                return self.intentions["debilitate"]
            else:
                return self.intentions["drain"]
        else:
            # Step 2: Poke or Zap
            if random.random() < 0.60:
                return self.intentions["poke"]
            else:
                return self.intentions["zap"]

"""
Giant Head - Act 3 Elite enemy
Counts down until "It Is Time" attack.
"""

import random

from enemies.base import Enemy
from enemies.act3.giant_head_intentions import (
    CountIntention,
    GlareIntention,
    ItIsTimeIntention,
)
from utils.types import EnemyType


class GiantHead(Enemy):
    """Giant Head - Elite enemy that counts down to devastating attacks."""

    enemy_type = EnemyType.ELITE

    def __init__(self):
        super().__init__(hp_range=(500, 500))
        
        # Register intentions
        self.add_intention(CountIntention(self))
        self.add_intention(GlareIntention(self))
        self.add_intention(ItIsTimeIntention(self))
        
        # Internal state
        self._turn_count = 0
        self._it_is_time_count = 0

    def determine_next_intention(self, floor: int = 1):
        """Determine next intention based on turn count.
        
        Giant Head pattern:
        - First 4 turns: 50/50 chance of Count or Glare
        - Turn 5+: Always It Is Time
        """
        self._turn_count += 1
        
        # After turn 4, always use It Is Time
        if self._turn_count > 4:
            self.current_intention = self.intentions["It Is Time"]
            return
        
        # First 4 turns: 50/50 chance
        # Can't use same move 3 times in a row
        last_moves = self.history_intentions[-2:] if len(self.history_intentions) >= 2 else []
        count_consecutive = last_moves.count("Count")
        glare_consecutive = last_moves.count("Glare")
        
        if count_consecutive >= 2:
            # Must use Glare
            self.current_intention = self.intentions["Glare"]
        elif glare_consecutive >= 2:
            # Must use Count
            self.current_intention = self.intentions["Count"]
        else:
            # 50/50 chance
            if random.random() < 0.5:
                self.current_intention = self.intentions["Count"]
            else:
                self.current_intention = self.intentions["Glare"]

    def on_combat_start(self, floor: int = 1):
        """Initialize combat state."""
        super().on_combat_start(floor)
        self._turn_count = 0
        self._it_is_time_count = 0

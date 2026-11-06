"""
Giant Head - Act 3 Elite enemy
Counts down until "It Is Time" attack.
"""
from engine.random_streams import get_rng


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
        super().__init__(hp_range=(500, 500)) # todo: 520 a8
        
        # Register intentions
        self.add_intention(CountIntention(self))
        self.add_intention(GlareIntention(self))
        self.add_intention(ItIsTimeIntention(self))
        
        # Internal state
        self._turn_count = 0
        self._selected_after_turn = -1
        self._it_is_time_count = 0

    def determine_next_intention(self, floor: int = 1):
        """Determine next intention based on turn count.
        
        Giant Head pattern:
        - First 4 turns: 50/50 chance of Count or Glare
        - Turn 5+: Always It Is Time
        """
        completed = len(self.history_intentions)
        if self._selected_after_turn == completed:
            return self.current_intention
        self._selected_after_turn = completed
        self._turn_count = completed + 1
        
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
            if get_rng("ai").random() < 0.5:
                self.current_intention = self.intentions["Count"]
            else:
                self.current_intention = self.intentions["Glare"]

    def on_combat_start(self, floor: int = 1):
        """Initialize combat state."""
        self._selected_after_turn = -1
        self._turn_count = 0
        self._it_is_time_count = 0
        super().on_combat_start(floor)
        # Giant Head starts with SlowPower
        from powers.definitions.slow import SlowPower
        self.add_power(SlowPower(owner=self))
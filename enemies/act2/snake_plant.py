"""
Snake Plant - Normal enemy (Act 2)
Plant enemy with debuff attacks.
"""
import random
from enemies.base import Enemy
from utils.types import EnemyType
from enemies.act2.snake_plant_intentions import (
    ChompChompIntention, EnfeeblingSporesIntention
)


class SnakePlant(Enemy):
    """Snake Plant - Plant enemy with debuff attacks."""
    
    enemy_type = EnemyType.NORMAL
    
    def __init__(self):
        super().__init__(
            hp_range=(75, 80)
        )
        
        # Track pattern mode (A9+ changes pattern after first Enfeebling Spores)
        self._has_used_spores = False
        
        # Register intentions
        self.add_intention(ChompChompIntention(self))
        self.add_intention(EnfeeblingSporesIntention(self))
    
    def on_combat_start(self, floor: int = 1):
        """Initialize combat state."""
        super().on_combat_start(floor)
        self._has_used_spores = False
    
    def determine_next_intention(self, floor: int = 1):
        """Determine next intention based on pattern."""
        # Get last intention
        last = self.history_intentions[-1] if self.history_intentions else None
        
        # Count consecutive Chomp Chomp
        def count_consecutive_chomp() -> int:
            count = 0
            for intent in reversed(self.history_intentions):
                if intent == "chomp_chomp":
                    count += 1
                else:
                    break
            return count
        
        chomp_count = count_consecutive_chomp()
        
        # Cannot use Chomp Chomp three times in a row
        # Cannot use Enfeebling Spores twice in a row
        
        # If last was spores, must use Chomp Chomp
        if last == "enfeebling_spores":
            self._has_used_spores = True
            return self.intentions["chomp_chomp"]
        
        # If Chomp Chomp used 3 times, must use Spores
        if chomp_count >= 2:
            self._has_used_spores = True
            return self.intentions["enfeebling_spores"]
        
        # Normal pattern: Chomp Chomp (60%), Enfeebling Spores (35%)
        # Note: The remaining 5% is likely an idle/unknown state
        roll = random.random()
        
        if roll < 0.60:
            return self.intentions["chomp_chomp"]
        elif roll < 0.95:  # 0.60 + 0.35
            self._has_used_spores = True
            return self.intentions["enfeebling_spores"]
        else:
            # Fallback to Chomp Chomp
            return self.intentions["chomp_chomp"]

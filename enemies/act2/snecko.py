"""
Snecko - Normal enemy (Act 2)
Snake enemy that confuses the player.
"""
import random
from enemies.base import Enemy
from utils.types import EnemyType
from enemies.act2.snecko_intentions import (
    PerplexingGlareIntention, BiteIntention, TailWhipIntention
)


class Snecko(Enemy):
    """Snecko - Snake enemy that confuses the player."""
    
    enemy_type = EnemyType.NORMAL
    
    def __init__(self):
        super().__init__(
            hp_range=(69, 74)
        )
        
        # Register intentions
        self.add_intention(PerplexingGlareIntention(self))
        self.add_intention(BiteIntention(self))
        self.add_intention(TailWhipIntention(self))
    
    def determine_next_intention(self, floor: int = 1):
        """Determine next intention based on pattern."""
        # Always starts with Perplexing Glare
        if not self.history_intentions:
            return self.intentions["perplexing_glare"]
        
        # Count consecutive Bites
        def count_consecutive_bite() -> int:
            count = 0
            for intent in reversed(self.history_intentions):
                if intent == "bite":
                    count += 1
                else:
                    break
            return count
        
        bite_count = count_consecutive_bite()
        
        # Cannot use Bite three times in a row
        if bite_count >= 2:
            return self.intentions["tail_whip"]
        
        # Normal pattern after first turn: Bite (60%), Tail Whip (40%)
        if random.random() < 0.60:
            return self.intentions["bite"]
        else:
            return self.intentions["tail_whip"]

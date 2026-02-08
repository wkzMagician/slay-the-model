"""
Spike Slime - Common enemy
Can split into smaller slimes when damaged.
"""
import random
from enemies.base import Enemy
from utils.types import EnemyType
from enemies.act1.spike_slime_intentions import LickIntention, FlameTackleIntention, SplitIntention


class SpikeSlime(Enemy):
    """Spike Slime (L) - Can split when HP reaches 50% or below."""
    
    enemy_type = EnemyType.NORMAL
    
    def __init__(self):
        super().__init__(
            hp_range=(28, 32)
        )
        
        # Register intentions
        self.add_intention(LickIntention(self))
        self.add_intention(FlameTackleIntention(self))
        self.add_intention(SplitIntention(self))
        
        # Track if split has been triggered
        self._split_triggered = False
    
    def determine_next_intention(self, floor: int = 1):
        """Determine next intention based on history.
        
        SpikeSlime pattern:
        - 30% Flame Tackle, 70% Lick
        - Cannot use same move three times in a row
        - If HP <= 50%, current intention changes to Split
        """
        # Check if HP threshold reached
        if self.hp <= self.max_hp / 2 and not self._split_triggered:
            self._split_triggered = True
            return self.intentions["split"]
        
        # If split already triggered, no more intentions (will be removed)
        if self._split_triggered:
            return self.intentions["lick"]  # Fallback
        
        # Count consecutive uses of last intention
        if not self.history_intentions:
            # First move: 30% Flame Tackle, 70% Lick
            roll = random.random()
            if roll < 0.30:
                return self.intentions["flame_tackle"]
            else:
                return self.intentions["lick"]
        
        last = self.history_intentions[-1]
        
        # Count consecutive uses
        consecutive_count = 0
        for intention in reversed(self.history_intentions):
            if intention == last:
                consecutive_count += 1
            else:
                break
        
        # Cannot use same move three times in a row
        if consecutive_count >= 2:
            # Must switch to the other move
            if last == "lick":
                return self.intentions["flame_tackle"]
            else:
                return self.intentions["lick"]
        
        # Normal pattern: 30% Flame Tackle, 70% Lick
        roll = random.random()
        if roll < 0.30:
            return self.intentions["flame_tackle"]
        else:
            return self.intentions["lick"]
    
    def on_damage_taken(self, damage: int, source=None, card=None, damage_type: str = "direct") -> int:
        """Check for split condition when taking damage."""
        # Call parent method first
        modified_damage = super().on_damage_taken(damage, source, card, damage_type)
        
        # Check if HP threshold reached and not already triggered
        if self.hp <= self.max_hp / 2 and not self._split_triggered:
            # Set split flag and change current intention to split
            self._split_triggered = True
            self.current_intention = self.intentions["split"]
        
        return modified_damage


class SpikeSlimeM(Enemy):
    """Spike Slime (M) - Smaller version after splitting."""
    
    enemy_type = EnemyType.NORMAL
    
    def __init__(self):
        super().__init__(
            hp_range=(14, 16)
        )
        
        # Register intentions (same as large but weaker)
        self.add_intention(LickIntention(self))
        self.add_intention(FlameTackleIntention(self))
    
    def determine_next_intention(self, floor: int = 1):
        """Determine next intention for medium slime.
        
        SpikeSlimeM pattern (same as large but no split):
        - 30% Flame Tackle, 70% Lick
        - Cannot use same move three times in a row
        """
        if not self.history_intentions:
            # First move: 30% Flame Tackle, 70% Lick
            roll = random.random()
            if roll < 0.30:
                return self.intentions["flame_tackle"]
            else:
                return self.intentions["lick"]
        
        last = self.history_intentions[-1]
        
        # Count consecutive uses
        consecutive_count = 0
        for intention in reversed(self.history_intentions):
            if intention == last:
                consecutive_count += 1
            else:
                break
        
        # Cannot use same move three times in a row
        if consecutive_count >= 2:
            # Must switch to the other move
            if last == "lick":
                return self.intentions["flame_tackle"]
            else:
                return self.intentions["lick"]
        
        # Normal pattern: 30% Flame Tackle, 70% Lick
        roll = random.random()
        if roll < 0.30:
            return self.intentions["flame_tackle"]
        else:
            return self.intentions["lick"]
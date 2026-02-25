"""
Spike Slime enemies - Large, Medium, and Small variants.
Large can split into smaller slimes when damaged.
"""
import random
from typing import List, TYPE_CHECKING
from enemies.base import Enemy
from utils.types import EnemyType
from enemies.act1.spike_slime_intentions import (
    LickIntention,
    TackleIntention,
    SplitIntention
)

if TYPE_CHECKING:
    from actions.base import Action


class SpikeSlimeL(Enemy):
    """Spike Slime (L) - Large variant that can split at 50% HP.
    
    According to doc: This is referenced in Slime Boss split,
    but the detailed pattern is not specified in the doc.
    Using similar pattern to AcidSlimeL.
    """
    
    enemy_type = EnemyType.NORMAL
    
    def __init__(self):
        super().__init__(
            hp_range=(64, 70) # todo: 67-73 >= ancension7
        )
        
        # Register intentions
        self.add_intention(LickIntention(self))
        self.add_intention(TackleIntention(self))
        self.add_intention(SplitIntention(self))
        
        # Track if split has been triggered
        self._split_triggered = False
    
    def determine_next_intention(self, floor: int = 1):
        """Determine next intention based on history.
        
        SpikeSlimeL pattern (similar to Acid Slime L):
        - 30% Tackle, 70% Lick
        - Cannot use Tackle twice in a row
        - Cannot use other moves 3 times in a row
        - If HP <= 50%, current intention changes to Split
        """
        # Check if HP threshold reached
        if self.hp <= self.max_hp / 2 and not self._split_triggered:
            return self.intentions["split"]
        
        # If split already triggered, no more intentions (will be removed)
        if self._split_triggered:
            return self.intentions["lick"]  # Fallback
        
        # First move: 30% Tackle, 70% Lick
        if not self.history_intentions:
            roll = random.random()
            if roll < 0.30:
                return self.intentions["tackle"]
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
        
        # Cannot use Tackle twice in a row
        if last == "tackle" and consecutive_count >= 1:
            return self.intentions["lick"]
        
        # Cannot use other moves 3 times in a row
        if consecutive_count >= 2:
            if last == "lick":
                return self.intentions["tackle"]
        
        # Normal pattern: 30% Tackle, 70% Lick
        roll = random.random()
        if roll < 0.30:
            return self.intentions["tackle"]
        else:
            return self.intentions["lick"]
    
    def on_damage_taken(self, damage: int, source=None, card=None, damage_type: str = "direct") -> List['Action']:
        """Check for split condition when taking damage."""
        actions = super().on_damage_taken(damage, source, card, damage_type)
        
        # Check if HP threshold reached and not already triggered
        if self.hp <= self.max_hp / 2 and not self._split_triggered:
            self._split_triggered = True
            self.current_intention = self.intentions["split"]
        
        return actions


class SpikeSlimeM(Enemy):
    """Spike Slime (M) - Medium variant.
    
    Used after SpikeSlimeL splits.
    """
    
    enemy_type = EnemyType.NORMAL
    
    def __init__(self):
        super().__init__(
            hp_range=(28, 32) # todo: 29-34 >= ancension7
        )
        
        # Register intentions
        self.add_intention(LickIntention(self))
        self.add_intention(TackleIntention(self))
    
    def determine_next_intention(self, floor: int = 1):
        """Determine next intention for medium slime.
        
        SpikeSlimeM pattern:
        - 30% Tackle, 70% Lick
        - Cannot use same move 3 times in a row
        """
        # First move: 30% Tackle, 70% Lick
        if not self.history_intentions:
            roll = random.random()
            if roll < 0.30:
                return self.intentions["tackle"]
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
        
        # Cannot use same move 3 times in a row
        if consecutive_count >= 2:
            if last == "lick":
                return self.intentions["tackle"]
            else:
                return self.intentions["lick"]
        
        # Normal pattern: 30% Tackle, 70% Lick
        roll = random.random()
        if roll < 0.30:
            return self.intentions["tackle"]
        else:
            return self.intentions["lick"]


class SpikeSlimeS(Enemy):
    """Spike Slime (S) - Small variant.
    
    According to doc:
    - Tackle: Deals 5 damage (6 on A2+)
    - Health: 10-14 (11-15 on A7+)
    """
    
    enemy_type = EnemyType.NORMAL
    
    def __init__(self):
        super().__init__(
            hp_range=(10, 14) # todo: 11-15 >= ancension7
        )
        
        # Register intentions
        self.add_intention(LickIntention(self))
        self.add_intention(TackleIntention(self))
    
    def determine_next_intention(self, floor: int = 1):
        """Determine next intention for small slime.
        
        SpikeSlimeS pattern:
        - Tackle only (no Lick mentioned in doc)
        - But pattern shows both Lick and Tackle
        """
        # First move: 50% Lick, 50% Tackle
        if not self.history_intentions:
            roll = random.random()
            if roll < 0.50:
                return self.intentions["lick"]
            else:
                return self.intentions["tackle"]
        
        last = self.history_intentions[-1]
        
        # Count consecutive uses
        consecutive_count = 0
        for intention in reversed(self.history_intentions):
            if intention == last:
                consecutive_count += 1
            else:
                break
        
        # Cannot use same move 3 times in a row
        if consecutive_count >= 2:
            if last == "lick":
                return self.intentions["tackle"]
            else:
                return self.intentions["lick"]
        
        # Normal pattern: 50% Lick, 50% Tackle
        roll = random.random()
        if roll < 0.50:
            return self.intentions["lick"]
        else:
            return self.intentions["tackle"]

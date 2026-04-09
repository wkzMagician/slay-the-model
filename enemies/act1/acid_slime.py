"""
Acid Slime enemies - Large, Medium, and Small variants.
Large and Medium can split into smaller slimes when damaged.
"""
from engine.runtime_api import add_action, add_actions
import random
from typing import List, TYPE_CHECKING
from enemies.base import Enemy
from utils.types import EnemyType
from enemies.act1.acid_slime_intentions import (
    CorrosiveSpitIntention,
    LickIntention,
    TackleIntention,
    SplitIntention
)

if TYPE_CHECKING:
    from actions.base import Action


class AcidSlimeL(Enemy):
    """Acid Slime (L) - Large variant that can split at 50% HP."""
    
    enemy_type = EnemyType.NORMAL
    
    def __init__(self):
        super().__init__(
            hp_range=(65, 69) # todo: 68-72 >= ancension 7
        )
        
        # Register intentions
        self.add_intention(CorrosiveSpitIntention(self))
        self.add_intention(LickIntention(self))
        self.add_intention(TackleIntention(self))
        self.add_intention(SplitIntention(self))
        
        # Track if split has been triggered
        self._split_triggered = False
    
    def determine_next_intention(self, floor: int = 1):
        """Determine next intention based on history.
        
        AcidSlimeL pattern:
        - 30% Corrosive Spit
        - 40% Lick
        - 30% Tackle
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
        
        # First move: 30% Spit, 40% Lick, 30% Tackle
        if not self.history_intentions:
            roll = random.random()
            if roll < 0.30:
                return self.intentions["corrosive_spit"]
            elif roll < 0.70:
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
        
        # Cannot use Tackle twice in a row
        if last == "tackle" and consecutive_count >= 1:
            # Must switch to another move
            roll = random.random()
            if roll < 0.43:  # 30/70 for corrosive_spit
                return self.intentions["corrosive_spit"]
            else:
                return self.intentions["lick"]
        
        # Cannot use other moves 3 times in a row
        if consecutive_count >= 2:
            # Must switch to a different move
            if last == "corrosive_spit":
                roll = random.random()
                if roll < 0.5:
                    return self.intentions["lick"]
                else:
                    return self.intentions["tackle"]
            elif last == "lick":
                roll = random.random()
                if roll < 0.5:
                    return self.intentions["corrosive_spit"]
                else:
                    return self.intentions["tackle"]
        
        # Normal pattern: 30% Spit, 40% Lick, 30% Tackle
        roll = random.random()
        if roll < 0.30:
            return self.intentions["corrosive_spit"]
        elif roll < 0.70:
            return self.intentions["lick"]
        else:
            return self.intentions["tackle"]
    
    def on_any_hp_lost(self, amount: int, source=None, card=None) -> None:
        """Check for split condition when taking damage."""
        actions = []
        # Check if HP threshold reached and not already triggered
        if self.hp <= self.max_hp / 2 and not self._split_triggered:
            self._split_triggered = True
            self.current_intention = self.intentions["split"]
        
        from engine.game_state import game_state
        
        add_actions(actions)
        
class AcidSlimeM(Enemy):
    """Acid Slime (M) - Medium variant, cannot split."""
    
    enemy_type = EnemyType.NORMAL
    
    def __init__(self):
        super().__init__(
            hp_range=(28, 32) # todo: 29-34 >= ancension7
        )
        
        # Register intentions
        self.add_intention(CorrosiveSpitIntention(self))
        self.add_intention(LickIntention(self))
        self.add_intention(TackleIntention(self))
    
    def determine_next_intention(self, floor: int = 1):
        """Determine next intention based on history.
        
        AcidSlimeM pattern:
        - 30% Corrosive Spit
        - 40% Lick
        - 30% Tackle
        - Cannot use Lick twice in a row
        - Cannot use other moves 3 times in a row
        - On A17+: 40% Spit, 20% Lick, 40% Tackle
        """
        # First move: 30% Spit, 40% Lick, 30% Tackle
        if not self.history_intentions:
            roll = random.random()
            if roll < 0.30:
                return self.intentions["corrosive_spit"]
            elif roll < 0.70:
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
        
        # Cannot use Lick twice in a row
        if last == "lick" and consecutive_count >= 1:
            roll = random.random()
            if roll < 0.5:
                return self.intentions["corrosive_spit"]
            else:
                return self.intentions["tackle"]
        
        # Cannot use other moves 3 times in a row
        if consecutive_count >= 2:
            # Must switch to a different move
            if last == "corrosive_spit":
                roll = random.random()
                if roll < 0.5:
                    return self.intentions["lick"]
                else:
                    return self.intentions["tackle"]
            elif last == "tackle":
                roll = random.random()
                if roll < 0.5:
                    return self.intentions["corrosive_spit"]
                else:
                    return self.intentions["lick"]
        
        # Normal pattern: 30% Spit, 40% Lick, 30% Tackle
        roll = random.random()
        if roll < 0.30:
            return self.intentions["corrosive_spit"]
        elif roll < 0.70:
            return self.intentions["lick"]
        else:
            return self.intentions["tackle"]


class AcidSlimeS(Enemy):
    """Acid Slime (S) - Small variant."""
    
    enemy_type = EnemyType.NORMAL
    
    def __init__(self):
        super().__init__(
            hp_range=(8, 12) # todo: 9-13 >= ancensioin7
        )
        
        # Register intentions
        self.add_intention(LickIntention(self))
        self.add_intention(TackleIntention(self))
    
    def determine_next_intention(self, floor: int = 1):
        """Determine next intention based on history.
        
        AcidSlimeS pattern:
        - 50% Lick
        - 50% Tackle
        - Cannot use same move 3 times in a row
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

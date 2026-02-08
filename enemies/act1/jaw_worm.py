"""
Jaw Worm - Common enemy
Quick attacks with moderate damage.
"""
import random
from enemies.base import Enemy
from utils.types import EnemyType
from enemies.act1.jaw_worm_intentions import ChompIntention, BellowIntention, ThrashIntention


class JawWorm(Enemy):
    """Jaw Worm - Quick attacks with moderate damage"""
    
    enemy_type = EnemyType.NORMAL
    
    def __init__(self):
        super().__init__(
            hp_range=(44, 48)
        )
        
        # Register intentions
        self.add_intention(ChompIntention(self))
        self.add_intention(BellowIntention(self))
        self.add_intention(ThrashIntention(self))
    
    def determine_next_intention(self, floor: int = 1):
        """Determine next intention based on history and floor."""
        # First turn logic
        if not self.history_intentions:
            # Check if in Act 3+ (floor 17+)
            if floor >= 17:
                # 45% Bellow, 30% Thrash, 25% Chomp
                roll = random.random()
                if roll < 0.45:
                    return self.intentions["bellow"]
                elif roll < 0.75:  # 0.45 + 0.30
                    return self.intentions["thrash"]
                else:
                    return self.intentions["chomp"]
            else:
                # Always start with Chomp in Act 1-2
                return self.intentions["chomp"]
        
        # Get last intention
        last = self.history_intentions[-1]
        
        # Check for consecutive Thrash
        thrash_count = 0
        for intention in reversed(self.history_intentions):
            if intention == "thrash":
                thrash_count += 1
            else:
                break
        
        # After Chomp: 59% Bellow, 41% Thrash
        if last == "chomp":
            roll = random.random()
            if roll < 0.59:
                return self.intentions["bellow"]
            else:
                return self.intentions["thrash"]
        
        # After Bellow: 56% Thrash, 44% Chomp
        elif last == "bellow":
            roll = random.random()
            if roll < 0.56:
                return self.intentions["thrash"]
            else:
                return self.intentions["chomp"]
        
        # After Thrash
        elif last == "thrash":
            # If Thrash used 2 times in a row
            if thrash_count >= 2:
                # 64% Bellow, 36% Chomp
                roll = random.random()
                if roll < 0.64:
                    return self.intentions["bellow"]
                else:
                    return self.intentions["chomp"]
            else:
                # 45% Bellow, 30% Thrash, 25% Chomp
                roll = random.random()
                if roll < 0.45:
                    return self.intentions["bellow"]
                elif roll < 0.75:  # 0.45 + 0.30
                    return self.intentions["thrash"]
                else:
                    return self.intentions["chomp"]
        
        # Fallback
        return self.intentions["chomp"]

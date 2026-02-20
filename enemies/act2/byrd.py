"""
Byrd - Normal enemy (Act 2)
Flying bird that uses aerial attacks.
"""
import random
from enemies.base import Enemy
from utils.types import EnemyType
from enemies.act2.byrd_intentions import (
    PeckIntention, CawIntention, SwoopIntention,
    StunnedIntention, HeadbuttIntention, GoAirborneIntention
)


class Byrd(Enemy):
    """Byrd - Flying bird enemy with aerial attack patterns."""
    
    enemy_type = EnemyType.NORMAL
    
    def __init__(self):
        super().__init__(
            hp_range=(22, 28)
        )
        
        # Track flying state
        self._is_flying = True
        self._grounded_pattern_index = 0
        
        # Register intentions
        self.add_intention(PeckIntention(self))
        self.add_intention(CawIntention(self))
        self.add_intention(SwoopIntention(self))
        self.add_intention(StunnedIntention(self))
        self.add_intention(HeadbuttIntention(self))
        self.add_intention(GoAirborneIntention(self))
    
    def on_combat_start(self, floor: int = 1):
        """Initialize combat state."""
        super().on_combat_start(floor)
        self._is_flying = True
        self._grounded_pattern_index = 0
    
    def determine_next_intention(self, floor: int = 1):
        """Determine next intention based on flying state and history."""
        # Check if still flying (has flying power with amount > 0)
        flying_power = self.get_power("flying")
        self._is_flying = flying_power is not None and flying_power > 0
        
        if self._is_flying:
            return self._determine_flying_intention()
        else:
            return self._determine_grounded_intention()
    
    def _determine_flying_intention(self):
        """Determine intention while flying."""
        # Get last intention
        last = self.history_intentions[-1] if self.history_intentions else None
        
        # Cannot use Caw and Swoop twice in a row
        # Cannot use Peck three times in a row
        peck_count = 0
        for intention in reversed(self.history_intentions):
            if intention == "peck":
                peck_count += 1
            else:
                break
        
        # Byrd never starts with Swoop
        if not self.history_intentions:
            roll = random.random()
            if roll < 0.50:
                return self.intentions["peck"]
            elif roll < 0.80:  # 0.50 + 0.30
                return self.intentions["caw"]
            else:
                return self.intentions["peck"]  # Don't use swoop first
        
        # After patterns
        roll = random.random()
        
        # Can't use Caw twice in a row
        if last == "caw":
            if roll < 0.50:
                return self.intentions["peck"]
            else:
                return self.intentions["swoop"]
        
        # Can't use Swoop twice in a row
        if last == "swoop":
            if roll < 0.50:
                return self.intentions["peck"]
            else:
                return self.intentions["caw"]
        
        # Can't use Peck three times in a row
        if peck_count >= 2:
            if roll < 0.60:  # 30/(30+20)
                return self.intentions["caw"]
            else:
                return self.intentions["swoop"]
        
        # Normal pattern: Peck 50%, Caw 30%, Swoop 20%
        if roll < 0.50:
            return self.intentions["peck"]
        elif roll < 0.80:  # 0.50 + 0.30
            return self.intentions["caw"]
        else:
            return self.intentions["swoop"]
    
    def _determine_grounded_intention(self):
        """Determine intention while grounded - follows fixed pattern."""
        # Pattern: Stunned -> Headbutt -> Go Airborne
        result = None
        
        if self._grounded_pattern_index == 0:
            result = self.intentions["stunned"]
        elif self._grounded_pattern_index == 1:
            result = self.intentions["headbutt"]
        else:
            result = self.intentions["go_airborne"]
        
        self._grounded_pattern_index += 1
        
        # After Go Airborne, reset and return to flying pattern
        if self._grounded_pattern_index > 2:
            self._grounded_pattern_index = 0
            self._is_flying = True
        
        return result

"""
Spheric Guardian - Normal enemy (Act 2/3)
Defensive orb enemy with alternating patterns.
"""
import random
from enemies.base import Enemy
from utils.types import EnemyType
from enemies.act2.spheric_guardian_intentions import (
    ActivateIntention, DebuffAttackIntention, SlamIntention, HardenIntention
)


class SphericGuardian(Enemy):
    """Spheric Guardian - Defensive orb enemy."""
    
    enemy_type = EnemyType.NORMAL
    
    def __init__(self):
        super().__init__(
            hp_range=(20)
        )
        
        # Pattern: Activate -> Debuff Attack -> alternate Slam/Harden
        self._pattern_index = 0
        
        # Register intentions
        self.add_intention(ActivateIntention(self))
        self.add_intention(DebuffAttackIntention(self))
        self.add_intention(SlamIntention(self))
        self.add_intention(HardenIntention(self))
    
    def on_combat_start(self, floor: int = 1):
        """Initialize combat state."""
        super().on_combat_start(floor)
        self._pattern_index = 0
        
        # Initial powers and block
        from powers.definitions.barricade import BarricadePower
        from powers.definitions.artifact import ArtifactPower
        
        self.add_power(BarricadePower(owner=self))
        self.add_power(ArtifactPower(amount=3, owner=self))
        self.gain_block(40)
    
    def determine_next_intention(self, floor: int = 1):
        """Determine next intention based on fixed pattern."""
        # Always starts with Activate
        if self._pattern_index == 0:
            self._pattern_index = 1
            return self.intentions["activate"]
        
        # Second is Debuff Attack
        if self._pattern_index == 1:
            self._pattern_index = 2
            return self.intentions["debuff_attack"]
        
        # After that, alternate Slam and Harden
        if self._pattern_index % 2 == 0:
            self._pattern_index += 1
            return self.intentions["slam"]
        else:
            self._pattern_index += 1
            return self.intentions["harden"]

"""
The Hexaghost - Act 1 Final Boss
Complex attack pattern with Burn cards.
"""
from typing import List, TYPE_CHECKING
from enemies.base import Enemy
from utils.types import EnemyType
from enemies.act1.the_hexaghost_intentions import (
    ActivateIntention,
    DividerIntention,
    SearIntention,
    TackleIntention,
    InflameIntention,
    InfernoIntention
)

if TYPE_CHECKING:
    from actions.base import Action


class TheHexaghost(Enemy):
    """The Hexaghost - Act 1 Final Boss with complex attack pattern."""
    
    enemy_type = EnemyType.BOSS
    
    def __init__(self):
        super().__init__(
            hp_range=(250, 250)  # Boss has fixed HP
        )
        
        # Register intentions
        self.add_intention(ActivateIntention(self))
        self.add_intention(DividerIntention(self))
        self.add_intention(SearIntention(self))
        self.add_intention(TackleIntention(self))
        self.add_intention(InflameIntention(self))
        self.add_intention(InfernoIntention(self))
        
        # Pattern tracking
        # Turn 1: Activate, Turn 2: Divider
        # Then pattern: Sear -> Tackle -> Sear -> Inflame -> Tackle -> Sear -> Inferno
        self._turn_count = 0
        
        # Track if Inferno has been used - subsequent Sear Burns will be upgraded
        self._used_inferno = False
    
    def determine_next_intention(self, floor: int = 1):
        """Determine next intention based on turn count.
        
        Turn 1: Activate
        Turn 2: Divider
        Then repeats: Sear -> Tackle -> Sear -> Inflame -> Tackle -> Sear -> Inferno
        """
        self._turn_count += 1
        
        # First turn: Activate
        if self._turn_count == 1:
            return self.intentions["activate"]
        
        # Second turn: Divider
        if self._turn_count == 2:
            return self.intentions["divider"]
        
        # Main pattern (starts from turn 3)
        pattern = ["sear", "tackle", "sear", "inflame", "tackle", "sear", "inferno"]
        pattern_index = (self._turn_count - 3) % len(pattern)
        
        return self.intentions[pattern[pattern_index]]

"""
Slime Boss - Act 1 Boss
Splits into two Large Slimes when HP reaches 50%.
"""
from engine.runtime_api import add_action, add_actions
from typing import List, TYPE_CHECKING
from enemies.base import Enemy
from utils.types import EnemyType
from enemies.act1.slime_boss_intentions import (
    GoopSprayIntention,
    PreparingIntention,
    SlamIntention,
    SplitIntention
)

if TYPE_CHECKING:
    from actions.base import Action


class SlimeBoss(Enemy):
    """Slime Boss - Act 1 Boss that splits at 50% HP."""
    
    enemy_type = EnemyType.BOSS
    
    def __init__(self):
        super().__init__(
            hp_range=(140, 140)  # todo: 150 a9
        )
        
        # Register intentions
        self.add_intention(GoopSprayIntention(self))
        self.add_intention(PreparingIntention(self))
        self.add_intention(SlamIntention(self))
        self.add_intention(SplitIntention(self))
        
        # Pattern tracking
        self._pattern_index = 0
        self._split_triggered = False
    
    def determine_next_intention(self, floor: int = 1):
        """Determine next intention based on pattern and HP.
        
        Pattern: Goop Spray -> Preparing -> Slam
        When HP <= 50%, current intent changes to Split.
        """
        # Check for split
        if self.hp <= self.max_hp / 2 and not self._split_triggered:
            return self.intentions["split"]
        
        # Normal pattern
        pattern = ["goop_spray", "preparing", "slam"]
        intention_name = pattern[self._pattern_index % len(pattern)]
        self._pattern_index += 1
        
        return self.intentions[intention_name]
    
    def on_any_hp_lost(self, amount: int, source=None, card=None) -> None:
        """Check for split trigger when taking damage."""
        actions = []
        # Check if HP threshold reached
        if self.hp <= self.max_hp / 2 and not self._split_triggered:
            self._split_triggered = True
            self.current_intention = self.intentions["split"]
        
        from engine.game_state import game_state
        
        add_actions(actions)
        

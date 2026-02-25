"""Time Eater - Act 3 Boss."""
import random
from typing import Optional

from enemies.act3.time_eater_intentions import (
    Reverberate,
    HeadSlam,
    Ripple,
    Haste,
)
from enemies.base import Enemy
from utils.types import EnemyType


class TimeEater(Enemy):
    """Time Eater is a Boss found at the end of Act 3.
    
    Pattern:
    - Starts with Time Warp power (whenever player plays 12 cards, 
      ends their turn and Time Eater gains 1 Strength)
    - Use Haste when reduced to below half HP (only once per combat)
    - Reverberate (45%), HeadSlam (35%), Ripple (20%)
    - No Reverberate 3x in a row, no HeadSlam/Ripple 2x in a row
    """
    
    enemy_type = EnemyType.BOSS
    
    def __init__(self):
        super().__init__(hp_range=(456, 456)) # todo: 480 a9
        self.add_intention(Reverberate(self))
        self.add_intention(HeadSlam(self))
        self.add_intention(Ripple(self))
        self.add_intention(Haste(self))
        
        self._haste_used = False
        self._haste_triggered = False  # Flag to trigger Haste next turn
    
    def on_combat_start(self, floor: int):
        """Initialize combat state and add Time Warp power."""
        super().on_combat_start(floor)
        self._haste_used = False
        self._haste_triggered = False
        
        # Add Time Warp power at combat start
        from powers.definitions.time_warp import TimeWarpPower
        self.add_power(TimeWarpPower(amount=1, owner=self))
    
    def on_damage_taken(self, damage: int, source=None, card=None, damage_type=None):
        """Check if Haste should be triggered next turn."""
        super().on_damage_taken(damage, source, card, damage_type)
        if not self._haste_used and self.hp <= self.max_hp // 2:
            # Set flag to trigger Haste next turn instead of immediately
            self._haste_triggered = True
            self._haste_used = True
    
    def determine_next_intention(self, floor: int) -> Optional[str]:
        """Determine the next intention based on AI pattern."""
        # If Haste was triggered by damage, use Haste next turn
        if self._haste_triggered:
            self._haste_triggered = False  # Reset flag
            return self.intentions["Haste"]
        
        # If HP below half and Haste not used, use Haste
        if not self._haste_used and self.hp <= self.max_hp // 2:
            self._haste_used = True
            self._haste_triggered = False
            return self.intentions["Haste"]
        
        # Get last move for constraint checking
        last_move = self.history_intentions[-1] if self.history_intentions else None
        
        # Count consecutive uses
        reverberate_count = 0
        head_slam_count = 0
        ripple_count = 0
        
        for move in reversed(self.history_intentions):
            if move == "Reverberate":
                reverberate_count += 1
            elif move == "Head Slam":
                head_slam_count += 1
            elif move == "Ripple":
                ripple_count += 1
            else:
                break
        
        # Random selection with constraints
        while True:
            roll = random.random()
            if roll < 0.45:  # 45% Reverberate
                if reverberate_count < 2:  # Not 3x in a row
                    return self.intentions["Reverberate"]
            elif roll < 0.80:  # 35% Head Slam
                if head_slam_count < 1:  # Not 2x in a row
                    return self.intentions["Head Slam"]
            else:  # 20% Ripple
                if ripple_count < 1:  # Not 2x in a row
                    return self.intentions["Ripple"]

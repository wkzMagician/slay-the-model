"""
Fungi Beast - Common enemy
Gains strength over time. Applies Vulnerable on death.
"""
import random
from typing import List, TYPE_CHECKING
from enemies.base import Enemy
from utils.types import EnemyType
from enemies.act1.fungi_beast_intentions import BiteIntention, GrowIntention

if TYPE_CHECKING:
    from actions.base import Action


class FungiBeast(Enemy):
    """Fungi Beast - Gains strength and applies Vulnerable on death."""
    
    enemy_type = EnemyType.NORMAL
    
    def __init__(self):
        super().__init__(
            hp_range=(22, 28)
        )
        
        # Register intentions
        self.add_intention(BiteIntention(self))
        self.add_intention(GrowIntention(self))
        
        # Spore Cloud: On death, applies 2 Vulnerable
        self._spore_cloud_stacks = 2
    
    def determine_next_intention(self, floor: int = 1):
        """Determine next intention based on history.
        
        Fungi Beast pattern:
        - 60% Bite, 40% Grow
        - Cannot use Bite 3 times in a row
        - Cannot use Grow 2 times in a row
        """
        # First turn: random choice
        if not self.history_intentions:
            roll = random.random()
            if roll < 0.60:
                return self.intentions["bite"]
            else:
                return self.intentions["grow"]
        
        # Count consecutive uses
        last = self.history_intentions[-1]
        consecutive_count = 0
        for intention in reversed(self.history_intentions):
            if intention == last:
                consecutive_count += 1
            else:
                break
        
        # Cannot use Bite 3 times in a row
        if last == "bite" and consecutive_count >= 2:
            return self.intentions["grow"]
        
        # Cannot use Grow 2 times in a row
        if last == "grow" and consecutive_count >= 1:
            return self.intentions["bite"]
        
        # Normal pattern: 60% Bite, 40% Grow
        roll = random.random()
        if roll < 0.60:
            return self.intentions["bite"]
        else:
            return self.intentions["grow"]
    
    def on_death(self) -> List['Action']:
        """Apply Spore Cloud on death: applies 2 Vulnerable to player."""
        from actions.combat import ApplyPowerAction
        from engine.game_state import game_state
        
        actions = super().on_death()
        
        if game_state and game_state.player:
            actions.append(
                ApplyPowerAction(
                    power="Vulnerable",
                    target=game_state.player,
                    amount=self._spore_cloud_stacks,
                    duration=self._spore_cloud_stacks
                )
            )
        
        return actions

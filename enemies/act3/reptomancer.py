"""Reptomancer enemy for Slay the Model."""

import random
from typing import List, Optional

from enemies.act3.reptomancer_intentions import (
    SpawnDaggerIntention, BigBiteIntention, SnakeStrikeIntention
)
from enemies.act3.dagger import Dagger
from enemies.base import Enemy
from utils.types import EnemyType


class Reptomancer(Enemy):
    """Reptomancer is a normal Enemy found exclusively in Act 3.
    
    Special mechanics:
    - Summons Daggers that deal damage and explode
    - Always starts with Spawn Dagger
    - Cannot have more than 4 Daggers in play
    """
    
    enemy_type = EnemyType.NORMAL
    
    def __init__(self):
        super().__init__(hp_range=(180, 190)) # todo: 190-200 a8
        self._turn_count = 0
        self._last_intention = None
        
        # Register intentions
        self.add_intention(SpawnDaggerIntention(self))
        self.add_intention(BigBiteIntention(self))
        self.add_intention(SnakeStrikeIntention(self))
    
    def determine_next_intention(self, floor: int) -> Optional[str]:
        """Determine next intention based on pattern."""
        self._turn_count += 1
        
        if self._turn_count == 1:
            # Always starts with Spawn Dagger
            self._last_intention = "Spawn Dagger"
            return self.intentions["Spawn Dagger"]
        
        # Equal chance of Snake Strike, Big Bite, Spawn Dagger
        # Cannot use Snake Strike or Big Bite twice in a row
        # Cannot use Spawn Dagger three times in a row
        # If 4 Daggers in play and Spawn Dagger chosen, use Snake Strike instead
        
        choices = ["Snake Strike", "Big Bite", "Spawn Dagger"]
        
        # Filter based on constraints
        if self._last_intention == "Snake Strike":
            choices.remove("Snake Strike")
        if self._last_intention == "Big Bite":
            choices.remove("Big Bite")
        
        # Check if Spawn Dagger was used twice in a row
        if len(self.history_intentions) >= 2:
            if self.history_intentions[-1] == "Spawn Dagger" and self.history_intentions[-2] == "Spawn Dagger":
                if "Spawn Dagger" in choices:
                    choices.remove("Spawn Dagger")
        
        # Check dagger count
        from engine.game_state import game_state
        dagger_count = sum(1 for e in game_state.current_combat.enemies if isinstance(e, Dagger))
        if dagger_count >= 4 and "Spawn Dagger" in choices:
            choices.remove("Spawn Dagger")
            if "Snake Strike" not in choices:
                choices.append("Snake Strike")
        
        choice = random.choice(choices)
        self._last_intention = choice
        return choice

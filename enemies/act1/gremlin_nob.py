# -*- coding: utf-8 -*-
"""Gremlin Nob - Act 1 Elite enemy"""

import random
from enemies.base import Enemy
from utils.types import EnemyType
from utils.registry import register
from enemies.act1.gremlin_nob_intentions import (
    BellowIntention, SkullBashIntention, BullRushIntention
)


@register("enemy")
class GremlinNob(Enemy):
    enemy_type = EnemyType.ELITE
    
    def __init__(self, ascension: int = 0):
        if ascension >= 18:
            hp = random.randint(92, 97)
        else:
            hp = random.randint(82, 87)
        
        super().__init__(hp_range=(hp, hp))
        self.ascension = ascension
        self.turn_count = 0
        self.bull_rush_count = 0
        self.last_action = None
        
        skull_damage = 8 if ascension >= 9 else 6
        bull_damage = 18 if ascension >= 9 else 14
        
        # Register intentions with keys
        self.add_intention(BellowIntention(self))
        self.add_intention(SkullBashIntention(self, skull_damage))
        self.add_intention(BullRushIntention(self, bull_damage))
        
        from powers.definitions.enrage import EnragePower
        self.add_power(EnragePower(2, owner=self))
    
    def determine_next_intention(self, floor: int = 1):
        """Determine next intention based on turn count and ascension.
        
        Also updates turn tracking state for next decision.
        """
        # Determine intention based on current turn_count, then update state
        current_turn = self.turn_count
        
        if current_turn == 0:
            intention = self.intentions["bellow"]
        elif self.ascension >= 18:
            # Fixed pattern: Skull Bash -> Bull Rush -> Bull Rush -> repeat
            pattern_index = (current_turn - 1) % 3
            if pattern_index == 0:
                intention = self.intentions["skull_bash"]
            else:
                intention = self.intentions["bull_rush"]
        else:
            # Normal: 33% Skull Bash, 67% Bull Rush (cannot do 3 Bull Rush in a row)
            if self.last_action == "bull" and self.bull_rush_count >= 2:
                intention = self.intentions["skull_bash"]
            else:
                intention = self.intentions["skull_bash"] if random.random() < 0.33 else self.intentions["bull_rush"]
        
        # Update tracking state for next turn
        if intention == self.intentions["bull_rush"]:
            self.bull_rush_count = self.bull_rush_count + 1 if self.last_action == "bull" else 1
            self.last_action = "bull"
        else:
            self.bull_rush_count = 0
            self.last_action = "skull"
        
        # Increment turn count after deciding (for next turn's intention)
        self.turn_count += 1
        
        return intention

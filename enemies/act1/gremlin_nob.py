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
        
        self._bellow = BellowIntention(self)
        self._skull = SkullBashIntention(self, skull_damage)
        self._bull = BullRushIntention(self, bull_damage)
        
        from powers.definitions.enrage import EnragePower
        self.add_power(EnragePower(2, owner=self))
    
    def get_current_intention(self):
        if self.turn_count == 0:
            return self._bellow
        if self.ascension >= 18:
            return self._skull if (self.turn_count - 1) % 3 == 0 else self._bull
        if self.last_action == "bull" and self.bull_rush_count >= 2:
            return self._skull
        return self._skull if random.random() < 0.33 else self._bull
    
    def execute_turn(self):
        intention = self.get_current_intention()
        self.turn_count += 1
        
        if isinstance(intention, BullRushIntention):
            self.bull_rush_count = self.bull_rush_count + 1 if self.last_action == "bull" else 1
            self.last_action = "bull"
        else:
            self.bull_rush_count = 0
            self.last_action = "skull"
        
        if intention:
            return intention.execute()
        return None

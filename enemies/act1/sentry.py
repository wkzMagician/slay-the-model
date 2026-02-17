# -*- coding: utf-8 -*-
"""Sentry - Act 1 Elite enemy"""

import random
from enemies.base import Enemy
from utils.types import EnemyType
from utils.registry import register
from enemies.act1.sentry_intentions import BoltIntention, BeamIntention


@register("enemy")
class Sentry(Enemy):
    enemy_type = EnemyType.ELITE
    
    def __init__(self, ascension: int = 0, is_middle: bool = False):
        if ascension >= 3:
            hp = random.randint(40, 42)
        else:
            hp = random.randint(38, 40)
        
        super().__init__(hp_range=(hp, hp))
        self.ascension = ascension
        self.is_middle = is_middle
        self.turn_count = 0
        
        beam_damage = 10 if ascension >= 3 else 9
        dazed_count = 3 if ascension >= 3 else 2
        
        self._bolt = BoltIntention(self, dazed_count)
        self._beam = BeamIntention(self, beam_damage)
    
    def get_current_intention(self):
        if self.is_middle:
            return self._beam if self.turn_count % 2 == 0 else self._bolt
        return self._bolt if self.turn_count % 2 == 0 else self._beam
    
    def execute_turn(self):
        intention = self.get_current_intention()
        self.turn_count += 1
        if intention:
            return intention.execute()
        return None

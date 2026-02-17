# -*- coding: utf-8 -*-
"""Lagavulin - Act 1 Elite enemy"""

import random
from enemies.base import Enemy
from utils.types import EnemyType
from utils.registry import register
from enemies.act1.lagavulin_intentions import (
    SleepIntention, StunnedIntention, 
    AttackIntention, SiphonSoulIntention
)


@register("enemy")
class Lagavulin(Enemy):
    enemy_type = EnemyType.ELITE
    
    def __init__(self, ascension: int = 0):
        if ascension >= 3:
            hp = random.randint(112, 115)
        else:
            hp = random.randint(109, 111)
        
        super().__init__(hp_range=(hp, hp))
        self.ascension = ascension
        self.is_sleeping = True
        self.is_stunned = False
        self.turns_without_damage = 0
        self.attack_pattern_index = 0
        
        from powers.definitions.metallicize import MetallicizePower
        self.add_power(MetallicizePower(8, owner=self))
        
        damage = 20 if ascension >= 3 else 18
        dex_loss = 2 if ascension >= 3 else 1
        str_gain = 2 if ascension >= 3 else 1
        
        self._sleep = SleepIntention(self)
        self._stunned = StunnedIntention(self)
        self._attack = AttackIntention(self, damage)
        self._siphon = SiphonSoulIntention(self, dex_loss, str_gain)
    
    def get_current_intention(self):
        if self.is_sleeping:
            return self._sleep
        if self.is_stunned:
            return self._stunned
        return self._attack if self.attack_pattern_index == 0 else self._siphon
    
    def execute_turn(self):
        if self.is_sleeping:
            return None
        if self.is_stunned:
            self.is_stunned = False
            return None
        
        intention = self.get_current_intention()
        if intention:
            intention.execute()
        self.attack_pattern_index = 1 - self.attack_pattern_index
    
    def on_damage_taken(self, amount: int, source=None, card=None, damage_type=None):
        if self.is_sleeping and amount > 0:
            self.is_sleeping = False
            self.is_stunned = True
            self.turns_without_damage = 0
            self.powers = [p for p in self.powers if p.name != "Metallicize"]
    
    def on_turn_start(self):
        if self.is_sleeping:
            self.turns_without_damage += 1
            if self.turns_without_damage >= 3:
                self.is_sleeping = False
                self.powers = [p for p in self.powers if p.name != "Metallicize"]

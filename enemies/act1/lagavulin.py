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
        
        # Register intentions with keys
        self.add_intention(SleepIntention(self))
        self.add_intention(StunnedIntention(self))
        self.add_intention(AttackIntention(self, damage))
        self.add_intention(SiphonSoulIntention(self, dex_loss, str_gain))
    
    def determine_next_intention(self, floor: int = 1):
        """Determine next intention based on state."""
        if self.is_sleeping:
            return self.intentions["sleep"]
        if self.is_stunned:
            return self.intentions["stunned"]
        if self.attack_pattern_index == 0:
            return self.intentions["attack"]
        return self.intentions["siphon_soul"]
    
    def execute_turn(self):
        if self.is_sleeping:
            return None
        if self.is_stunned:
            self.is_stunned = False
            return None
        
        intention = self.determine_next_intention()
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

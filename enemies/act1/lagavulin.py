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
        """Determine next intention based on state.
        
        Also handles natural wake-up after 3 turns without damage.
        Counter increments at START of turn for correct intention display.
        """
        # Handle natural wake-up: increment counter first
        if self.is_sleeping:
            self.turns_without_damage += 1
            if self.turns_without_damage >= 3:
                # Wake up now - show correct intention this turn
                self.is_sleeping = False
                self.powers = [p for p in self.powers if p.name != "Metallicize"]
                # Fall through to attack pattern below
        
        if self.is_sleeping:
            return self.intentions["sleep"]
        if self.is_stunned:
            return self.intentions["stunned"]
        if self.attack_pattern_index == 0:
            return self.intentions["attack"]
        return self.intentions["siphon_soul"]
    
    def execute_intention(self):
        """Override to handle state transitions since base combat calls execute_intention, not execute_turn."""
        from actions.base import Action
        
        # Handle sleeping state - just do nothing
        # Note: wake-up counter is handled in determine_next_intention()
        if self.is_sleeping:
            return []
        
        # Handle stunned state - clear stun and do nothing this turn
        if self.is_stunned:
            self.is_stunned = False
            return []
        
        # Execute the current intention
        actions = []
        if self.current_intention:
            actions = self.current_intention.execute()
        
        # Toggle attack pattern index for next turn
        self.attack_pattern_index = 1 - self.attack_pattern_index
        
        return actions
    
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

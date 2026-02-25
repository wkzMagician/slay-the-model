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
    
    def __init__(self, ascension: int = 0, start_awake: bool = False):
        if ascension >= 8:
            hp = random.randint(112, 115)
        else:
            hp = random.randint(109, 111)
        
        super().__init__(hp_range=(hp, hp))
        self.ascension = ascension
        self.is_sleeping = not start_awake  # Can start awake for Dead Adventurer event
        self.is_stunned = False
        self.turns_without_damage = 0
        # For normal: starts at 0 (Attack -> Attack -> Siphon -> repeat)
        # For start_awake: starts at 2 (Siphon -> Attack -> Attack -> repeat)
        self.attack_pattern_index = 2 if start_awake else 0
        
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
    
    def on_combat_start(self, floor: int = 1) -> None:
        """Gain Metallicize 8 and Block 8 on combat start."""
        super().on_combat_start(floor)
        self.gain_block(8)
    
    def determine_next_intention(self, floor: int = 1):
        """Determine next intention based on state.
        
        Handles:
        - Natural wake-up after 3 turns without damage
        - Attack pattern: Attack -> Attack -> Siphon Soul (or reversed if start_awake)
        - Stunned state clearing after one turn
        """
        # Handle natural wake-up: increment counter first
        if self.is_sleeping:
            self.turns_without_damage += 1
            if self.turns_without_damage >= 3:
                # Wake up now - show correct intention this turn
                self.is_sleeping = False
                self.powers = [p for p in self.powers if p.name != "Metallicize"]
        
        if self.is_sleeping:
            return self.intentions["sleep"]
        
        if self.is_stunned:
            # Clear stunned state after returning stun intention
            self.is_stunned = False
            return self.intentions["stunned"]
        
        # Attack pattern: toggle between Attack and Siphon Soul
        if self.attack_pattern_index < 2: # 0, 1
            intention = self.intentions["attack"]
        else:
            intention = self.intentions["siphon_soul"]
        
        # Toggle pattern index for next turn
        self.attack_pattern_index = (self.attack_pattern_index + 1) % 3
        
        return intention
    
    def on_damage_taken(self, amount: int, source=None, card=None, damage_type=None):
        """When damaged while sleeping, wake up and become stunned for one turn."""
        if self.is_sleeping and amount > 0:
            self.is_sleeping = False
            self.is_stunned = True
            self.turns_without_damage = 0
            self.powers = [p for p in self.powers if p.name != "Metallicize"]

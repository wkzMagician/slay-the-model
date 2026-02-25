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
        if ascension >= 8:
            hp = random.randint(39, 45)
        else:
            hp = random.randint(38, 42)
        
        super().__init__(hp_range=(hp, hp))
        self.ascension = ascension
        self.is_middle = is_middle
        self.turn_count = 0
        
        beam_damage = 10 if ascension >= 3 else 9
        dazed_count = 3 if ascension >= 3 else 2
        
        # Register intentions with keys
        self.add_intention(BoltIntention(self, dazed_count))
        self.add_intention(BeamIntention(self, beam_damage))
        
        # Add Artifact power (negates 1 debuff)
        from powers.definitions.artifact import ArtifactPower
        self.add_power(ArtifactPower(1, owner=self))
    
    def determine_next_intention(self, floor: int = 1):
        """Determine next intention based on position (side/middle).
        
        Also updates turn count for next decision.
        """
        if self.is_middle:
            # Middle: Beam first, then Bolt
            intention = self.intentions["beam"] if self.turn_count % 2 == 0 else self.intentions["bolt"]
        else:
            # Side: Bolt first, then Beam
            intention = self.intentions["bolt"] if self.turn_count % 2 == 0 else self.intentions["beam"]
        
        # Increment turn count for next decision
        self.turn_count += 1
        
        return intention

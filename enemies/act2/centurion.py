"""
Centurion - Normal enemy (Act 2)
Warrior that protects the Mystic.
"""
import random
from enemies.base import Enemy
from utils.types import EnemyType
from enemies.act2.centurion_intentions import (
    SlashIntention, ProtectIntention, FuryIntention
)


class Centurion(Enemy):
    """Centurion - Warrior enemy that protects Mystic."""
    
    enemy_type = EnemyType.NORMAL
    
    def __init__(self):
        super().__init__(
            hp_range=(76, 80)
        )
        
        # Register intentions
        self.add_intention(SlashIntention(self))
        self.add_intention(ProtectIntention(self))
        self.add_intention(FuryIntention(self))
    
    def determine_next_intention(self, floor: int = 1):
        """Determine next intention based on Mystic status."""
        from engine.game_state import game_state
        
        # Check if Mystic is alive
        mystic_alive = False
        if game_state and game_state.combat:
            for enemy in game_state.combat.enemies:
                if enemy.__class__.__name__ == 'Mystic' and enemy.is_alive:
                    mystic_alive = True
                    break
        
        # Get last intention
        last = self.history_intentions[-1] if self.history_intentions else None
        
        # Count consecutive same moves
        def count_consecutive(intention_name: str) -> int:
            count = 0
            for intent in reversed(self.history_intentions):
                if intent == intention_name:
                    count += 1
                else:
                    break
            return count
        
        # If Mystic is alive: Slash (60%), Protect (20%)
        if mystic_alive:
            # Can't use same move three times in a row
            slash_count = count_consecutive("slash")
            protect_count = count_consecutive("protect")
            
            if slash_count >= 2:
                return self.intentions["protect"]
            if protect_count >= 2:
                return self.intentions["slash"]
            
            roll = random.random()
            if roll < 0.60:
                return self.intentions["slash"]
            else:
                return self.intentions["protect"]
        
        # If Mystic is dead: Slash (60%), Fury (20%)
        else:
            slash_count = count_consecutive("slash")
            fury_count = count_consecutive("fury")
            
            if slash_count >= 2:
                return self.intentions["fury"]
            if fury_count >= 2:
                return self.intentions["slash"]
            
            roll = random.random()
            if roll < 0.60:
                return self.intentions["slash"]
            else:
                return self.intentions["fury"]

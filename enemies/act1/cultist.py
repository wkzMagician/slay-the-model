"""
Cultist - Common enemy
Quick attacks with weak damage.
"""
from enemies.base import Enemy
from utils.types import EnemyType
from enemies.act1.cultist_intentions import CultistRitualIntention, CultistAttackIntention


class Cultist(Enemy):
    """Cultist - Quick attacks with weak damage"""
    
    enemy_type = EnemyType.NORMAL
    
    def __init__(self):
        super().__init__(
            hp_range=(40, 44)
        )
        
        # Register intentions
        self.add_intention(CultistRitualIntention(self))
        self.add_intention(CultistAttackIntention(self))
    
    def determine_next_intention(self, floor: int = 1):
        """Determine next intention based on history.
        
        Cultist pattern:
        - First turn: Always Ritual
        - After Ritual: Always Attack
        - After Attack: Always Attack
        """
        # First turn: Always Ritual
        if not self.history_intentions:
            return self.intentions["ritual"]
        
        # After first turn: Always Attack
        return self.intentions["attack"]

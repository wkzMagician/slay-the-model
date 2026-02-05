"""
The Guardian - Boss enemy
First boss. High damage, lots of HP.
"""
from entities.enemy import Enemy


class TheGuardian(Enemy):
    """The Guardian - First boss of the game"""
    
    def __init__(self):
        super().__init__(
            name="The Guardian",
            max_hp=200,
            damage=25,
            is_elite=False,
            is_boss=True
        )
    
    def __str__(self):
        return f"{self.name} ({self.current_hp}/{self.max_hp} HP)"

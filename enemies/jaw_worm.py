"""
Jaw Worm - Common enemy
Quick attacks with moderate damage.
"""
from entities.enemy import Enemy


class JawWorm(Enemy):
    """Jaw Worm - Quick attacks with moderate damage"""
    
    def __init__(self):
        super().__init__(
            name="Jaw Worm",
            max_hp=46,
            damage=10,
            is_elite=False,
            is_boss=False
        )
    
    def __str__(self):
        return f"{self.name} ({self.current_hp}/{self.max_hp} HP)"

"""
Cultist - Common enemy
Quick attacks with weak damage.
"""
from entities.enemy import Enemy


class Cultist(Enemy):
    """Cultist - Quick attacks with weak damage"""
    
    def __init__(self):
        super().__init__(
            name="Cultist",
            max_hp=42,
            damage=6,
            is_elite=False,
            is_boss=False
        )
    
    def __str__(self):
        return f"{self.name} ({self.current_hp}/{self.max_hp} HP)"

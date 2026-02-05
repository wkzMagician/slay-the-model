"""
Louse Slaver - Common enemy
Deals 12 damage per attack. Slow but hits hard.
"""
from entities.enemy import Enemy


class LouseSlaver(Enemy):
    """Louse Slaver - Deals 12 damage per attack"""
    
    def __init__(self):
        super().__init__(
            name="Louse Slaver",
            max_hp=82,
            damage=12,
            is_elite=False,
            is_boss=False
        )
    
    def __str__(self):
        return f"{self.name} ({self.current_hp}/{self.max_hp} HP)"

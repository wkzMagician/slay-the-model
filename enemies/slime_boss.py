"""
Slime Boss - Second boss
Split into 2 slimes that each deal moderate damage.
"""
from entities.enemy import Enemy


class SlimeBoss(Enemy):
    """Slime Boss - Second boss that splits into 2 enemies"""
    
    def __init__(self):
        super().__init__(
            name="Slime Boss",
            max_hp=140,
            damage=8,
            is_elite=False,
            is_boss=True
        )
    
    def __str__(self):
        return f"{self.name} ({self.current_hp}/{self.max_hp} HP)"

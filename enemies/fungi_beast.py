"""
Fungi Beast - Elite enemy
Slow but deals high damage and has more HP.
"""
from entities.enemy import Enemy


class FungiBeast(Enemy):
    """Fungi Beast - Elite enemy with high damage and HP"""
    
    def __init__(self):
        super().__init__(
            name="Fungi Beast",
            max_hp=88,
            damage=16,
            is_elite=True,
            is_boss=False
        )
    
    def __str__(self):
        return f"{self.name} ({self.current_hp}/{self.max_hp} HP)"

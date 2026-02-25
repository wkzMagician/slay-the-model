"""Taskmaster - Act 2 Elite enemy."""

from typing import List

from enemies.act2.taskmaster_intentions import ScouringWhip
from enemies.base import Enemy
from utils.types import EnemyType


class Taskmaster(Enemy):
    """Elite enemy found in Act 2 (Slavers encounter).
    
    Only uses Scouring Whip attack.
    Found with Red Slaver and Blue Slaver.
    Also found in The Colosseum event with Gremlin Nob.
    """
    
    enemy_type = EnemyType.ELITE
    
    def __init__(self):
        super().__init__(hp_range=(54, 46)) # todo: 57-64 a8
        
        # Register intentions
        self.add_intention(ScouringWhip(self))
    
    def determine_next_intention(self, floor: int) -> None:
        """Taskmaster only has one attack."""
        self.current_intention = self.intentions["Scouring Whip"]

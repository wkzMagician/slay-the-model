"""Exploder enemy for Act 3."""

from enemies.act3.exploder_intentions import Attack, Explode
from enemies.base import Enemy
from utils.types import EnemyType


class Exploder(Enemy):
    """Exploder enemy - explodes after 2 attacks."""

    enemy_type = EnemyType.NORMAL

    def __init__(self):
        super().__init__(hp_range=(30, 30)) # todo: 30-35 a7
        self.add_intention(Attack(self))
        self.add_intention(Explode(self))
        self._turn_count = 0

    def on_combat_start(self, floor: int):
        """Reset turn count at combat start."""
        super().on_combat_start(floor)
        self._turn_count = 0

    def determine_next_intention(self, floor: int):
        """Determine next intention based on turn count.
        
        Pattern: Attack -> Attack -> Explode
        """
        self._turn_count += 1

        if self._turn_count <= 2:
            self.current_intention = self.intentions["Attack"]
        else:
            self.current_intention = self.intentions["Explode"]

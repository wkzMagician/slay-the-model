"""Orb Walker enemy - Act 3 Normal enemy."""

from enemies.base import Enemy
from enemies.act3.orb_walker_intentions import Laser, Claw
from utils.types import EnemyType


class OrbWalker(Enemy):
    """Orb Walker is a normal Enemy encountered exclusively in Act 3."""

    enemy_type = EnemyType.NORMAL

    def __init__(self):
        super().__init__(hp_range=(52, 58))
        self.add_intention(Laser(self))
        self.add_intention(Claw(self))

    def determine_next_intention(self, floor: int):
        """Determine next intention based on pattern.

        Pattern:
        - Laser (66% chance)
        - Claw (34% chance)
        Cannot use either action three times in a row.
        """
        import random

        # Check for repeated moves
        if len(self.history_intentions) >= 3:
            last_three = self.history_intentions[-3:]
            if all(i == "Laser" for i in last_three):
                self.current_intention = self.intentions["Claw"]
                return
            if all(i == "Claw" for i in last_three):
                self.current_intention = self.intentions["Laser"]
                return

        # Random selection
        if random.random() < 0.66:
            self.current_intention = self.intentions["Laser"]
        else:
            self.current_intention = self.intentions["Claw"]

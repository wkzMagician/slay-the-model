"""Corrupt Heart - Act 4 Final Boss."""

import random
from typing import Optional

from enemies.act4.corrupt_heart_intentions import (
    BeatOfDeathPower,
    BloodShots,
    BuffHeart,
    Debilitate,
    Echo,
)
from enemies.base import Enemy
from utils.types import EnemyType


class CorruptHeart(Enemy):
    """Corrupt Heart is the final boss of the Spire (Act 4).

    Pattern:
    - Turn 1: Debilitate
    - From Turn 4, every 3 turns: Buff
    - Other turns: 50/50 pair order of Blood Shots and Echo
    """
    
    enemy_type = EnemyType.BOSS
    
    def __init__(self):
        super().__init__(hp_range=(750, 750)) # todo: 800 a9
        self.add_intention(Debilitate(self))
        self.add_intention(BloodShots(self))
        self.add_intention(Echo(self))
        self.add_intention(BuffHeart(self))

        self._turn_number = 0
        self._pair_sequence = []
        self._pair_index = 0
        self._buff_count = 0
    
    def on_combat_start(self, floor: int):
        """Initialize combat state."""
        super().on_combat_start(floor)
        self._turn_number = 0
        self._pair_sequence = []
        self._pair_index = 0
        self._buff_count = 0
        self.remove_power("Beat of Death")
        self.remove_power("Painful Stabs")
        self.add_power(BeatOfDeathPower(amount=1, owner=self))
    
    def determine_next_intention(self, floor: int) -> Optional[str]:
        """Follow documented Corrupt Heart turn pattern."""
        self._turn_number += 1

        if self._turn_number == 1:
            return self.intentions["Debilitate"]

        if self._turn_number >= 4 and (self._turn_number - 4) % 3 == 0:
            return self.intentions["Buff"]

        if self._pair_index >= len(self._pair_sequence):
            self._pair_sequence = random.choice(
                [["Blood Shots", "Echo"], ["Echo", "Blood Shots"]]
            )
            self._pair_index = 0

        intention_name = self._pair_sequence[self._pair_index]
        self._pair_index += 1
        return intention_name

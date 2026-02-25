"""Spire Spear - Act 4 Elite."""

import random
from typing import TYPE_CHECKING, Optional

from enemies.act4.spire_spear_intentions import BurnStrike, Piercer, Skewer
from enemies.base import Enemy
from utils.types import EnemyType

if TYPE_CHECKING:
    from engine.back_attack_manager import BackAttackManager


class SpireSpear(Enemy):
    """Spire Spear is an Elite found in Act 4.

    Pattern:
    - Turn 1: Burn Strike
    - Every 3 turns from turn 2: Skewer
    - Other turns: 50/50 pair order of Burn Strike and Piercer

    Special mechanics (with Spire Shield):
    - BackAttackPower can transfer to Spear when player targets Shield
    - When either enemy dies, BackAttack and Surrounded are removed
    """
    
    enemy_type = EnemyType.ELITE
    
    def __init__(self):
        super().__init__(hp_range=(160, 160)) # todo: 180 a8
        self.add_intention(BurnStrike(self))
        self.add_intention(Skewer(self))
        self.add_intention(Piercer(self))

        self._turn_number = 0
        self._pair_sequence = []
        self._pair_index = 0
        self._back_attack_manager: Optional["BackAttackManager"] = None
    
    def on_combat_start(self, floor: int):
        """Initialize combat state."""
        super().on_combat_start(floor)
        self._turn_number = 0
        self._pair_sequence = []
        self._pair_index = 0
    
    def on_death(self):
        """Clean up BackAttack mechanics when Spear dies."""
        if self._back_attack_manager is not None:
            self._back_attack_manager.on_enemy_death(self)
            self._back_attack_manager = None
        super().on_death()
    
    def determine_next_intention(self, floor: int) -> Optional[str]:
        """Follow documented Spire Spear turn pattern."""
        self._turn_number += 1

        if self._turn_number == 1:
            return self.intentions["Burn Strike"]

        if self._turn_number >= 2 and (self._turn_number - 2) % 3 == 0:
            return self.intentions["Skewer"]

        if self._pair_index >= len(self._pair_sequence):
            self._pair_sequence = random.choice(
                [["Burn Strike", "Piercer"], ["Piercer", "Burn Strike"]]
            )
            self._pair_index = 0

        intention_name = self._pair_sequence[self._pair_index]
        self._pair_index += 1
        return intention_name

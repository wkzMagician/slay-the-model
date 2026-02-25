"""Darkling enemy for Slay the Model."""

import random
from typing import List, Optional

from enemies.act3.darkling_intentions import (
    Chomp,
    Harden,
    Nip,
    Reincarnate,
    Regrowing,
)
from enemies.base import Enemy
from powers.definitions.life_link import LifeLinkPower
from utils.types import EnemyType


class Darkling(Enemy):
    """Darkling is a normal Enemy found exclusively in Act 3.

    Special mechanics:
    - When HP reaches 0, becomes untargetable and uses Regrowing
    - Next turn uses Reincarnate to revive with 50% HP
    """

    enemy_type = EnemyType.NORMAL

    def __init__(self):
        super().__init__(hp_range=(48, 56)) # todo: 50-59 a7
        self._turn_count = 0
        self._is_regrowing = False
        self._is_middle = False  # Set if this is the middle Darkling
        self._consecutive_nip = 0
        self._consecutive_chomp = 0
        self._consecutive_harden = 0

        # Register intentions
        self.add_intention(Harden(self))
        self.add_intention(Nip(self))
        self.add_intention(Chomp(self))
        self.add_intention(Regrowing(self))
        self.add_intention(Reincarnate(self))

    def on_combat_start(self, floor: int = 1) -> None:
        """Initialize Darkling combat state."""
        super().on_combat_start(floor)
        self.add_power(LifeLinkPower(owner=self))

    def determine_next_intention(self, floor: int):
        """Determine next intention based on pattern."""
        # If regrowing, use Reincarnate
        if self._is_regrowing:
            return self.intentions["Reincarnate"]

        # Turn 1: 50/50 Nip or Harden
        if self._turn_count == 0:
            self._turn_count += 1
            if random.random() < 0.5:
                return self.intentions["Nip"]
            else:
                return self.intentions["Harden"]

        self._turn_count += 1

        # Middle Darkling cannot use Chomp
        if self._is_middle:
            return self._determine_middle_pattern()

        # Outer Darklings pattern
        # Nip 30%, Chomp 40%, Harden 30%
        # Cannot use Harden or Chomp twice in a row
        # Cannot use Nip three times in a row

        roll = random.random()

        # Check constraints
        can_nip = self._consecutive_nip < 2
        can_chomp = self._consecutive_chomp == 0
        can_harden = self._consecutive_harden == 0

        # Weighted selection with constraints
        if roll < 0.3 and can_nip:
            self._reset_consecutive()
            self._consecutive_nip = 1
            return self.intentions["Nip"]
        elif roll < 0.7 and can_chomp:
            self._reset_consecutive()
            self._consecutive_chomp = 1
            return self.intentions["Chomp"]
        elif can_harden:
            self._reset_consecutive()
            self._consecutive_harden = 1
            return self.intentions["Harden"]
        elif can_nip:
            self._reset_consecutive()
            self._consecutive_nip = 1
            return self.intentions["Nip"]
        elif can_chomp:
            self._reset_consecutive()
            self._consecutive_chomp = 1
            return self.intentions["Chomp"]
        else:
            return self.intentions["Nip"]

    def _determine_middle_pattern(self):
        """Determine pattern for middle Darkling (no Chomp)."""
        can_nip = self._consecutive_nip < 2
        can_harden = self._consecutive_harden == 0

        roll = random.random()

        if roll < 0.5 and can_nip:
            self._reset_consecutive()
            self._consecutive_nip = 1
            return self.intentions["Nip"]
        elif can_harden:
            self._reset_consecutive()
            self._consecutive_harden = 1
            return self.intentions["Harden"]
        else:
            self._reset_consecutive()
            self._consecutive_nip = 1
            return self.intentions["Nip"]

    def _reset_consecutive(self):
        """Reset consecutive counters."""
        self._consecutive_nip = 0
        self._consecutive_chomp = 0
        self._consecutive_harden = 0

    def on_damage_taken(self, damage: int, source=None, card=None,
                        damage_type: str = "direct") -> List:
        """Check if HP reaches 0 to start regrowing."""
        actions = super().on_damage_taken(
            damage, source=source, card=card, damage_type=damage_type
        )
        if self.hp <= 0:
            self.hp = 0
            self._is_regrowing = True
            self.current_intention = self.intentions["Regrowing..."]
        return actions

    def is_dead(self) -> bool:
        """Darkling only dies when no other linked enemy is alive."""
        if self.hp > 0:
            return False

        from engine.game_state import game_state

        combat = getattr(game_state, "current_combat", None)
        if not combat:
            return True

        for enemy in combat.enemies:
            if enemy is self:
                continue
            if enemy.hp > 0 and enemy.has_power("Life Link"):
                return False
        return True

    def execute_intention(self) -> List:
        """Execute current intention."""
        if self.current_intention is None:
            return []

        # If regrowing and about to reincarnate
        if self._is_regrowing and self.current_intention.name == "Reincarnate":
            actions = self.current_intention.execute()
            return actions

        return super().execute_intention()

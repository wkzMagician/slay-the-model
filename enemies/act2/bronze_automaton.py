"""Bronze Automaton boss enemy (Act 2)."""

import random
from enemies.base import Enemy
from enemies.act2.bronze_automaton_intentions import (
    SummonOrb,
    Hit,
    Repair,
    HyperBeam,
    Unsummon,
)
from utils.types import EnemyType


class BronzeAutomaton(Enemy):
    """Bronze Automaton is a boss found at the end of Act 2."""

    enemy_type = EnemyType.BOSS

    def __init__(self):
        super().__init__(hp_range=(300, 300))
        self.add_intention(SummonOrb(self))
        self.add_intention(Hit(self))
        self.add_intention(Repair(self))
        self.add_intention(HyperBeam(self))
        self.add_intention(Unsummon(self))
        self._pattern_index = 0

    def on_combat_start(self, floor: int):
        """Initialize combat state."""
        super().on_combat_start(floor)
        self._pattern_index = 0
        self.current_intention = self.intentions["Summon Orb"]

    def determine_next_intention(self, floor: int):
        """Determine next intention based on fixed pattern.

        Pattern: Summon Orb -> Hit -> Repair -> Hyper Beam -> Unsummon -> repeat
        """
        # Pattern: 0=Summon Orb (only once at start), 1=Hit, 2=Repair, 3=Hyper Beam, 4=Unsummon
        pattern = ["Hit", "Repair", "Hyper Beam", "Unsummon"]
        
        intention_name = pattern[self._pattern_index % 4]
        self.current_intention = self.intentions[intention_name]
        self._pattern_index += 1

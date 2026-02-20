"""Bronze Automaton boss enemy (Act 2)."""

from enemies.base import Enemy
from enemies.act2.bronze_automaton_intentions import (
    SpawnOrbs,
    Flail,
    Boost,
    HyperBeam,
    Stunned,
)
from utils.types import EnemyType


class BronzeAutomaton(Enemy):
    """Bronze Automaton is a boss found at the end of Act 2.

    Pattern:
    1. Spawn Orbs (start only)
    2. Flail
    3. Boost
    4. Flail
    5. Boost
    6. Hyper Beam
    7. Stunned
    Repeat 2-7

    On A17+: Stunned is replaced with Boost
    """

    enemy_type = EnemyType.BOSS

    def __init__(self):
        super().__init__(hp_range=(300, 300))
        self.add_intention(SpawnOrbs(self))
        self.add_intention(Flail(self))
        self.add_intention(Boost(self))
        self.add_intention(HyperBeam(self))
        self.add_intention(Stunned(self))
        self._pattern_index = 0
        self._first_turn = True

    def on_combat_start(self, floor: int):
        """Initialize combat state and add Artifact 3."""
        super().on_combat_start(floor)
        self._pattern_index = 0
        self._first_turn = True
        # Add Artifact 3 at combat start
        from powers.definitions.artifact import ArtifactPower
        self.add_power(ArtifactPower(), 3)
        self.current_intention = self.intentions["Spawn Orbs"]

    def determine_next_intention(self, floor: int):
        """Determine next intention based on fixed pattern.

        Pattern after Spawn Orbs:
        Flail -> Boost -> Flail -> Boost -> Hyper Beam -> Stunned -> repeat

        On A17+: Stunned is replaced with Boost
        """
        if self._first_turn:
            self._first_turn = False
            return  # First turn is always Spawn Orbs

        # Pattern: 0=Flail, 1=Boost, 2=Flail, 3=Boost, 4=Hyper Beam, 5=Stunned
        pattern = ["Flail", "Boost", "Flail", "Boost", "Hyper Beam", "Stunned"]
        
        # TODO: On A17+, replace Stunned with Boost
        # if ascension >= 17 and pattern_index % 6 == 5:
        #     intention_name = "Boost"
        # else:
        
        intention_name = pattern[self._pattern_index % 6]
        self.current_intention = self.intentions[intention_name]
        self._pattern_index += 1

    def get_hp_for_ascension(self, ascension: int) -> int:
        """Get HP based on ascension level.

        Base HP: 300
        A17+: 320
        """
        if ascension >= 17:
            return 320
        return 300
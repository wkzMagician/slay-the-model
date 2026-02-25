"""Donu - Act 3 Boss (fights alongside Deca)."""

from enemies.act3.donu_intentions import (
    CircleOfPower,
    Beam,
)
from enemies.base import Enemy
from utils.types import EnemyType


class Donu(Enemy):
    """Donu is a boss found at the end of Act 3.
    
    Fights alongside Deca. Donu focuses on buffing.
    
    Pattern:
    - Alternates between Circle of Power and Beam
    - Circle of Power: All enemies gain 3 Strength
    - Beam: Deals 10x2 damage (12x2 on A17+)
    
    Powers:
    - Artifact 2 (loses 1 on A17+)
    """
    
    enemy_type = EnemyType.BOSS
    
    def __init__(self):
        super().__init__(hp_range=(250, 250)) # todo: 265 a9
        self.add_intention(CircleOfPower(self))
        self.add_intention(Beam(self))
        self._use_circle_of_power = True  # Start with Circle of Power
    
    def on_combat_start(self, floor: int):
        """Initialize combat state and add Artifact."""
        super().on_combat_start(floor)
        self._use_circle_of_power = True
        
        # Add Artifact 2 at combat start
        from powers.definitions.artifact import ArtifactPower
        self.add_power(ArtifactPower(amount=2, owner=self))
    
    def determine_next_intention(self, floor: int):
        """Determine next intention - alternates between Circle of Power and Beam."""
        if self._use_circle_of_power:
            intention = self.intentions["Circle of Power"]
        else:
            intention = self.intentions["Beam"]
        self._use_circle_of_power = not self._use_circle_of_power
        return intention
    
    def get_hp_for_ascension(self, ascension: int) -> int:
        """Get HP based on ascension level.
        
        Base HP: 250
        A9+: 265
        """
        if ascension >= 9:
            return 265
        return 250
    
    def get_beam_damage(self, ascension: int) -> int:
        """Get Beam damage based on ascension level.
        
        Base: 10
        A17+: 12
        """
        if ascension >= 17:
            return 12
        return 10

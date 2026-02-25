"""Deca - Act 3 Boss (fights alongside Donu)."""

from enemies.act3.deca_intentions import (
    DecaBeam,
    SquareOfProtection,
)
from enemies.base import Enemy
from utils.types import EnemyType


class Deca(Enemy):
    """Deca is a boss found at the end of Act 3.
    
    Fights alongside Donu. Deca focuses on defense and debuffs.
    
    Pattern:
    - Alternates between Beam and Square of Protection
    - Beam: Deals 10x2 damage, adds 2 Dazed to discard pile (12x2 on A17+)
    - Square of Protection: All enemies gain 16 Block (and 1 Plated Armor on A17+)
    
    Powers:
    - Artifact 2 (loses 1 on A17+)
    """
    
    enemy_type = EnemyType.BOSS
    
    def __init__(self):
        super().__init__(hp_range=(250, 250)) # todo: 265 a9
        self.add_intention(DecaBeam(self))
        self.add_intention(SquareOfProtection(self))
        self._use_beam = True  # Start with Beam
        self._add_plated_armor = False  # Set in on_combat_start based on ascension
    
    def on_combat_start(self, floor: int):
        """Initialize combat state and add Artifact."""
        super().on_combat_start(floor)
        self._use_beam = True
        
        # Get ascension from game state
        from engine.game_state import game_state
        ascension = getattr(game_state, 'ascension', 0)
        
        # Add Artifact 2 at combat start (Artifact 1 on A17+)
        from powers.definitions.artifact import ArtifactPower
        artifact_stacks = 1 if ascension >= 17 else 2
        self.add_power(ArtifactPower(amount=artifact_stacks, owner=self))
        
        # Set plated armor flag for A17+
        self._add_plated_armor = ascension >= 17
    
    def determine_next_intention(self, floor: int):
        """Determine next intention - alternates between Beam and Square of Protection."""
        if self._use_beam:
            intention = self.intentions["Beam"]
        else:
            intention = self.intentions["Square of Protection"]
        self._use_beam = not self._use_beam
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

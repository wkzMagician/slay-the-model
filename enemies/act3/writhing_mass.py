"""Writhing Mass enemy for Slay the Model."""

import random
from typing import List, Optional, TYPE_CHECKING

from enemies.act3.writhing_mass_intentions import (
    MultiHit, DebuffAttackMass, BigHit, BlockAttackMass, ParasiteIntention
)
from enemies.base import Enemy
from utils.types import EnemyType

if TYPE_CHECKING:
    from actions.base import Action


class WrithingMass(Enemy):
    """Writhing Mass is a normal Enemy found in Act 3.
    
    Special mechanics:
    - First turn: equal chance of Multi Hit, Big Hit, or Debuff Attack
    - After: Parasite 10%, Block Attack 30%, Debuff Attack 30%, Big Hit 30%
    - Cannot use same move twice in a row
    """
    
    enemy_type = EnemyType.NORMAL
    
    def __init__(self):
        super().__init__(hp_range=(160, 160)) # 175 a7
        self._turn_count = 0
        self._last_intention = None
        
        # Register intentions
        self.add_intention(MultiHit(self))
        self.add_intention(DebuffAttackMass(self))
        self.add_intention(BigHit(self))
        self.add_intention(BlockAttackMass(self))
        self.add_intention(ParasiteIntention(self))
    
    def determine_next_intention(self, floor: int):
        """Determine next intention based on pattern."""
        self._turn_count += 1
        
        if self._turn_count == 1:
            # First turn: equal chance of Multi Hit, Big Hit, or Debuff Attack
            choice = random.choice(["Multi Hit", "Big Hit", "Debuff Attack"])
            self._last_intention = choice
            return self.intentions[choice]
        
        # After first turn:
        # Parasite 10%, Block Attack 30%, Debuff Attack 30%, Big Hit 30%
        roll = random.random()
        
        if roll < 0.1:  # 10% Parasite
            if self._last_intention != "Parasite":
                self._last_intention = "Parasite"
                return self.intentions["Parasite"]
        elif roll < 0.4:  # 30% Block Attack
            if self._last_intention != "Block Attack":
                self._last_intention = "Block Attack"
                return self.intentions["Block Attack"]
        elif roll < 0.7:  # 30% Debuff Attack
            if self._last_intention != "Debuff Attack":
                self._last_intention = "Debuff Attack"
                return self.intentions["Debuff Attack"]
        else:  # 30% Big Hit
            if self._last_intention != "Big Hit":
                self._last_intention = "Big Hit"
                return self.intentions["Big Hit"]
        
        # If we hit a repeat, try again with a different option
        available = ["Multi Hit", "Debuff Attack", "Big Hit", "Block Attack"]
        if self._last_intention in available:
            available.remove(self._last_intention)
        choice = random.choice(available)
        self._last_intention = choice
        return self.intentions[choice]
    
    def on_combat_start(self, floor: int = 1) -> None:
        """Called when combat starts.
        
        Apply Malleable and Reactive powers at the start of combat.
        
        Args:
            floor: Current floor number
        """
        super().on_combat_start(floor)
        
        # Apply Malleable 4
        from powers.definitions.malleable import MalleablePower
        self.add_power(MalleablePower(amount=4, owner=self))
        
        # Apply Reactive
        from powers.definitions.reactive import ReactivePower
        self.add_power(ReactivePower(owner=self))
    
    def on_damage_taken(self, damage: int, source=None, card=None, 
                        damage_type=None) -> List['Action']:
        """Called when enemy takes damage.
        
        Due to Reactive power, changes its intention when hit by attack damage.
        
        Args:
            damage: Amount of damage being taken
            source: Source of damage
            card: Card that caused damage
            damage_type: Type of damage
            
        Returns:
            List of actions to queue after taking damage
        """
        # Check for Reactive power - if hit by attack, change intention
        if damage > 0 and damage_type == "attack":
            # Check if we have Reactive power
            if self.get_power("Reactive"):
                # Change to a random different intention
                available = ["Multi Hit", "Debuff Attack", "Big Hit", 
                            "Block Attack", "Parasite"]
                if self._last_intention in available:
                    available.remove(self._last_intention)
                if available:
                    new_intention = random.choice(available)
                    self._last_intention = new_intention
                    # Update current_intention
                    if new_intention in self.intentions:
                        self.current_intention = self.intentions[new_intention]
        
        return []

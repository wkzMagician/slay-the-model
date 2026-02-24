"""Bronze Orb - Minion summoned by Bronze Automaton."""

import random
from enemies.base import Enemy
from utils.types import EnemyType
from enemies.act2.bronze_orb_intentions import Steal, SupportBeam, Beam


class BronzeOrb(Enemy):
    """Bronze Orb is a minion summoned only by the Bronze Automaton.
    
    This is a summoned minion and should not trigger on_fatal effects.
    """

    enemy_type = EnemyType.NORMAL

    def __init__(self):
        super().__init__(hp_range=(20, 21), is_minion=True)
        self.add_intention(Steal(self))
        self.add_intention(SupportBeam(self))
        self.add_intention(Beam(self))
        self._has_used_steal = False
        self._beam_count = 0
        self.stolen_cards = []  # Track stolen cards to return on death

    def on_combat_start(self, floor: int):
        """Initialize combat state."""
        super().on_combat_start(floor)
        self._has_used_steal = False
        self._beam_count = 0

    def determine_next_intention(self, floor: int):
        """Determine next intention based on pattern.
        
        Pattern:
        - 75% chance to use Steal until hit once
        - After Beam: 70% Support Beam, 30% Beam
        - Cannot use same attack twice in a row
        """
        last = self.history_intentions[-1] if self.history_intentions else None
        
        # First turn: use Steal (75% chance) or Beam (25%)
        if not self._has_used_steal:
            if random.random() < 0.75:
                self._has_used_steal = True
                self.current_intention = self.intentions["Steal"]
                return
        
        # After using Beam, 70% Support Beam, 30% Beam
        if last == "Beam":
            if random.random() < 0.70:
                self.current_intention = self.intentions["Support Beam"]
            else:
                self._beam_count += 1
                self.current_intention = self.intentions["Beam"]
            return
        
        # Cannot use same attack twice in a row
        if last == "Support Beam":
            self._beam_count += 1
            self.current_intention = self.intentions["Beam"]
        elif last == "Steal":
            self.current_intention = self.intentions["Support Beam"]
        else:
            # Default to Beam
            self._beam_count += 1
            self.current_intention = self.intentions["Beam"]
    
    def on_death(self):
        """Return stolen cards to player's draw pile."""
        from actions.card import AddCardAction
        actions = []
        for card in self.stolen_cards:
            actions.append(AddCardAction(card=card, dest_pile='hand'))
        return actions

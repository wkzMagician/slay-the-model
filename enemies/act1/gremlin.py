"""Gremlin enemies for the Gremlin Gang encounter.

Gremlin Gang is a 4-enemy encounter in Act 1 featuring 4 random gremlins
chosen from the 5 types defined here.

HP values based on Slay the Spire Ascension 0:
- Fat Gremlin: 13-17 HP
- Sneaky Gremlin: 9-12 HP
- Mad Gremlin: 9-12 HP
- Shield Gremlin: 12-15 HP
- Gremlin Wizard: 9-12 HP
"""

import random
from typing import Optional

from enemies.base import Enemy
from utils.types import EnemyType
from enemies.act1.gremlin_intentions import (
    FatGremlinSmashIntention,
    SneakyGremlinStabIntention,
    MadGremlinScratchIntention,
    ShieldGremlinProtectIntention,
    ShieldGremlinBashIntention,
    GremlinWizardChargeIntention,
    GremlinWizardUltimateBlastIntention,
)


class FatGremlin(Enemy):
    """Fat Gremlin - deals damage and applies Weak.
    
    Behavior: Always uses Smash (4 damage + 1 Weak).
    HP: 13-17
    """
    
    enemy_type = EnemyType.NORMAL
    
    def __init__(self, hp_range: tuple[int, int] = (13, 17)):
        super().__init__(hp_range)
        self.add_intention(FatGremlinSmashIntention(self))
    
    def determine_next_intention(self, current_floor: int = 1):
        """Fat Gremlin always smashes."""
        self.current_intention = self.intentions["fat_gremlin_smash"]


class SneakyGremlin(Enemy):
    """Sneaky Gremlin - deals medium damage.
    
    Behavior: Always uses Stab (9 damage).
    HP: 9-12
    """
    
    enemy_type = EnemyType.NORMAL
    
    def __init__(self, hp_range: tuple[int, int] = (9, 12)):
        super().__init__(hp_range)
        self.add_intention(SneakyGremlinStabIntention(self))
    
    def determine_next_intention(self, current_floor: int = 1):
        """Sneaky Gremlin always stabs."""
        self.current_intention = self.intentions["sneaky_gremlin_stab"]


class MadGremlin(Enemy):
    """Mad Gremlin - deals small damage, gains Strength when hit.
    
    Behavior: Always uses Scratch (5 damage). Gains 1 Strength when
    taking damage from an attack (enraged behavior).
    HP: 9-12
    """
    
    enemy_type = EnemyType.NORMAL
    
    def __init__(self, hp_range: tuple[int, int] = (9, 12)):
        super().__init__(hp_range)
        self.add_intention(MadGremlinScratchIntention(self))
    
    def determine_next_intention(self, current_floor: int = 1):
        """Mad Gremlin always scratches."""
        self.current_intention = self.intentions["mad_gremlin_scratch"]
    
    def on_take_damage(self, damage: int, source=None):
        """Gain 1 Strength when taking damage from attacks."""
        from engine.game_state import game_state
        from actions.combat import ApplyPowerAction
        
        # Call parent to actually take damage
        result = super().on_take_damage(damage, source)
        
        # Gain Strength when damaged by player attacks
        if damage > 0 and source == game_state.player:
            game_state.action_queue.add_action(
                ApplyPowerAction(
                    power="strength",
                    target=self,
                    amount=1,
                    duration=-1,
                )
            )
        
        return result


class ShieldGremlin(Enemy):
    """Shield Gremlin - alternates between block and attack.
    
    Behavior: Alternates between Protect (6 Block) and Bash (6 damage).
    HP: 12-15
    """
    
    enemy_type = EnemyType.NORMAL
    
    def __init__(self, hp_range: tuple[int, int] = (12, 15)):
        super().__init__(hp_range)
        self.add_intention(ShieldGremlinProtectIntention(self))
        self.add_intention(ShieldGremlinBashIntention(self))
        self._use_protect_next = True
    
    def determine_next_intention(self, current_floor: int = 1):
        """Shield Gremlin alternates between Protect and Bash."""
        if self._use_protect_next:
            self.current_intention = self.intentions["shield_gremlin_protect"]
        else:
            self.current_intention = self.intentions["shield_gremlin_bash"]
        self._use_protect_next = not self._use_protect_next


class GremlinWizard(Enemy):
    """Gremlin Wizard - charges for 2 turns then attacks.
    
    Behavior: Charges for 2 turns (no action), then uses Ultimate Blast
    (25 damage). Resets charge counter after attacking.
    HP: 9-12
    """
    
    enemy_type = EnemyType.NORMAL
    
    def __init__(self, hp_range: tuple[int, int] = (9, 12)):
        super().__init__(hp_range)
        self.add_intention(GremlinWizardChargeIntention(self))
        self.add_intention(GremlinWizardUltimateBlastIntention(self))
        self._charge_count = 0
        self._charge_threshold = 2
    
    def determine_next_intention(self, floor: int = 1):
        """Wizard charges for 2 turns, then blasts."""
        if self._charge_count >= self._charge_threshold:
            self.current_intention = self.intentions["gremlin_wizard_ultimate_blast"]
            self._charge_count = 0
        else:
            self.current_intention = self.intentions["gremlin_wizard_charge"]
            self._charge_count += 1
    
    def execute_intention(self, *args, **kwargs):
        """Execute intention and track charge state."""
        result = super().execute_intention(*args, **kwargs)
        return result

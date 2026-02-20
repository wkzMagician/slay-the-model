"""Corrupt Heart - Act 4 Final Boss."""

import random
from typing import Optional

from enemies.act4.corrupt_heart_intentions import Debilitate, AttackHeart, BloodShots, Echo, BuffHeart, Invoke
from enemies.base import Enemy
from utils.types import EnemyType


class CorruptHeart(Enemy):
    """Corrupt Heart is the final boss of the Spire (Act 4).
    
    Phase 1: Debilitate -> Invoke -> Attack -> repeat (until below 50% HP)
    Phase 2: Blood Shots -> Echo -> Attack -> repeat
    
    Special: Every 12 cards played by player triggers Beat of Death (1 damage).
    """
    
    enemy_type = EnemyType.BOSS
    
    def __init__(self):
        super().__init__(hp_range=(750, 800))
        self.add_intention(Debilitate(self))
        self.add_intention(Invoke(self))
        self.add_intention(AttackHeart(self))
        self.add_intention(BloodShots(self))
        self.add_intention(Echo(self))
        self.add_intention(BuffHeart(self))
        
        # Track pattern position and phase
        self._pattern_index = 0
        self._phase = 1
        self._cards_played = 0
        self.unique_cards_played = 0
        self._invincible_hp = 500  # Takes 1 damage per hit after invincible HP
    
    def on_combat_start(self, floor: int):
        """Initialize combat state."""
        super().on_combat_start(floor)
        self._pattern_index = 0
        self._phase = 1
        self._cards_played = 0
        self.unique_cards_played = 0
    
    def on_player_card_played(self, card):
        """Track cards played for Beat of Death and Debilitate."""
        self._cards_played += 1
        self.unique_cards_played += 1
        
        # Every 12 cards, deal 1 damage (Beat of Death)
        if self._cards_played % 12 == 0:
            from engine.game_state import game_state
            from actions.combat import AttackAction
            game_state.add_action(AttackAction(damage=1, target=game_state.player, source=self, damage_type="beat"))
    
    def take_damage(self, amount: int) -> int:
        """Override to handle invincibility (1 damage per hit after 500)."""
        if self._phase == 1:
            # Phase 1: Limited to 500 damage total
            actual_damage = min(amount, self._invincible_hp)
            self._invincible_hp -= actual_damage
            if self._invincible_hp <= 0:
                self._phase = 2
            return super().take_damage(actual_damage)
        else:
            # Phase 2: Normal damage
            return super().take_damage(amount)
    
    def determine_next_intention(self, floor: int) -> Optional[str]:
        """Follow phase-dependent pattern."""
        if self._phase == 1:
            # Phase 1: Debilitate -> Invoke -> Attack
            pattern = ["Debilitate", "Invoke", "Attack"]
        else:
            # Phase 2: Blood Shots -> Echo -> Buff -> Attack
            pattern = ["Blood Shots", "Echo", "Buff", "Attack"]
        
        intention_name = pattern[self._pattern_index % len(pattern)]
        self._pattern_index += 1
        return intention_name
    
    @property
    def invincible_hp(self) -> int:
        """Return remaining invincible HP."""
        return max(0, self._invincible_hp)

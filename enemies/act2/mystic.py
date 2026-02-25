"""
Mystic - Normal enemy (Act 2)
Support caster that heals and buffs allies.
"""
import random
from enemies.base import Enemy
from utils.types import EnemyType
from enemies.act2.mystic_intentions import (
    AttackIntention, BuffIntention, HealIntention
)


class Mystic(Enemy):
    """Mystic - Support caster enemy."""
    
    enemy_type = EnemyType.NORMAL
    
    def __init__(self):
        super().__init__(
            hp_range=(48, 56) # todo: 50-58 a7
        )
        
        # Track consecutive heal uses
        self._consecutive_heals = 0
        
        # Register intentions
        self.add_intention(AttackIntention(self))
        self.add_intention(BuffIntention(self))
        self.add_intention(HealIntention(self))
    
    def on_combat_start(self, floor: int = 1):
        """Initialize combat state."""
        super().on_combat_start(floor)
        self._consecutive_heals = 0
    
    def determine_next_intention(self, floor: int = 1):
        """Determine next intention based on ally health."""
        from engine.game_state import game_state
        
        # Check if any enemy is missing 16+ HP
        need_heal = False
        if game_state and game_state.combat:
            for enemy in game_state.combat.enemies:
                if enemy.hp > 0 and (enemy.max_hp - enemy.hp) >= 16:
                    need_heal = True
                    break
        
        # If heal needed and haven't used twice in a row
        if need_heal and self._consecutive_heals < 2:
            self._consecutive_heals += 1
            return self.intentions["heal"]
        
        # Reset heal counter when not using heal
        self._consecutive_heals = 0
        
        # Get last intention
        last = self.history_intentions[-1] if self.history_intentions else None
        
        # Count consecutive same moves
        def count_consecutive(intention_name: str) -> int:
            count = 0
            for intent in reversed(self.history_intentions):
                if intent == intention_name:
                    count += 1
                else:
                    break
            return count
        
        # Cannot use Attack or Buff three times in a row
        # Cannot use Attack twice in a row
        attack_count = count_consecutive("attack")
        buff_count = count_consecutive("buff")
        
        # Can't use Attack twice in a row
        if attack_count >= 1:
            return self.intentions["buff"]
        
        # Can't use Buff three times in a row
        if buff_count >= 2:
            return self.intentions["attack"]
        
        # Normal: Attack (60%), Buff (40%)
        if random.random() < 0.60:
            return self.intentions["attack"]
        else:
            return self.intentions["buff"]

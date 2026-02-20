"""
Shelled Parasite - Normal enemy (Act 2)
Armored parasite that heals itself.
"""
import random
from enemies.base import Enemy
from utils.types import EnemyType
from enemies.act2.shelled_parasite_intentions import (
    DoubleStrikeIntention, LifeSuckIntention, FeltIntention, StunnedIntention
)


class ShelledParasite(Enemy):
    """Shelled Parasite - Armored parasite enemy."""
    
    enemy_type = EnemyType.NORMAL
    
    def __init__(self):
        super().__init__(
            hp_range=(68, 72)
        )
        
        # Track stun state (can only happen once)
        self._has_been_stunned = False
        
        # Register intentions
        self.add_intention(DoubleStrikeIntention(self))
        self.add_intention(LifeSuckIntention(self))
        self.add_intention(FeltIntention(self))
        self.add_intention(StunnedIntention(self))
    
    def on_combat_start(self, floor: int = 1):
        """Initialize combat state."""
        super().on_combat_start(floor)
        self._has_been_stunned = False
    
    def on_damage_taken(self, damage: int, source=None) -> int:
        """Check if Plated Armor is broken (HP-based approximation)."""
        # TODO: Implement proper Plated Armor mechanic
        return super().on_damage_taken(damage, source)
    
    def determine_next_intention(self, floor: int = 1):
        """Determine next intention based on pattern."""
        # Cannot use Felt on first turn
        if not self.history_intentions:
            return self.intentions["double_strike"]
        
        # Get last intention
        last = self.history_intentions[-1]
        
        # Count consecutive same intentions
        def count_consecutive(intention_name: str) -> int:
            count = 0
            for intent in reversed(self.history_intentions):
                if intent == intention_name:
                    count += 1
                else:
                    break
            return count
        
        # Cannot use Double Strike or Life Suck three times in a row
        # Cannot use Felt twice in a row
        
        roll = random.random()
        
        # Felt has 20% chance but can't be used twice in a row
        if last != "felt" and roll < 0.20:
            return self.intentions["felt"]
        
        # Double Strike and Life Suck have 40% each
        double_strike_count = count_consecutive("double_strike")
        life_suck_count = count_consecutive("life_suck")
        
        # Can't use either three times in a row
        available_intents = []
        if double_strike_count < 2:
            available_intents.append(("double_strike", 0.40))
        if life_suck_count < 2:
            available_intents.append(("life_suck", 0.40))
        
        # Calculate adjusted probabilities
        total_prob = sum(p for _, p in available_intents)
        roll = random.random() * total_prob
        
        cumulative = 0
        for intent_name, prob in available_intents:
            cumulative += prob
            if roll < cumulative:
                return self.intentions[intent_name]
        
        # Fallback
        return self.intentions["double_strike"]

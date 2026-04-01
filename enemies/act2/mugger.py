"""
Mugger - Normal enemy (Act 2)
Thief that steals gold and escapes.
"""
import random
from enemies.base import Enemy
from powers.definitions.thievery import ThieveryPower
from utils.types import EnemyType
from enemies.act2.mugger_intentions import (
    MugIntention, LungeIntention, SmokeBombIntention, EscapeIntention
)


class Mugger(Enemy):
    """Mugger - Thief enemy that steals gold and escapes."""
    
    enemy_type = EnemyType.NORMAL
    
    # Same pattern as Looter (from Act 1)
    
    def __init__(self):
        super().__init__(
            hp_range=(48, 52) # todo: 50-54 a7
        )
        
        # Register intentions
        self.add_intention(MugIntention(self))
        self.add_intention(LungeIntention(self))
        self.add_intention(SmokeBombIntention(self))
        self.add_intention(EscapeIntention(self))
        
    def on_combat_start(self, floor: int = 1) -> None:
        """Called when combat starts - apply Thievery power."""
        super().on_combat_start(floor)
        
        # Apply Thievery power (15 gold on normal, 20 on Ascension 7+)
        thievery_amount = 15  # todo: Ascension 7+ value = 20
        thievery = ThieveryPower(amount=thievery_amount, owner=self)
        self.add_power(thievery)
        mug_intention = self.intentions.get("mug")
        if mug_intention is not None:
            mug_intention.base_amount = thievery_amount
    
    def determine_next_intention(self, floor: int = 1):
        """Determine next intention based on pattern (same as Looter)."""
        # First turn: always Mug
        if not self.history_intentions:
            return self.intentions["mug"]
        
        # Get last intention
        last = self.history_intentions[-1]
        
        # After Mug: 70% Lunge, 30% Smoke Bomb
        if last == "mug":
            if random.random() < 0.70:
                return self.intentions["lunge"]
            else:
                return self.intentions["smoke_bomb"]
        
        # After Lunge: 50% Mug, 35% Smoke Bomb, 15% Escape
        elif last == "lunge":
            roll = random.random()
            if roll < 0.50:
                return self.intentions["mug"]
            elif roll < 0.85:  # 0.50 + 0.35
                return self.intentions["smoke_bomb"]
            else:
                return self.intentions["escape"]
        
        # After Smoke Bomb: 60% Mug, 40% Lunge
        elif last == "smoke_bomb":
            if random.random() < 0.60:
                return self.intentions["mug"]
            else:
                return self.intentions["lunge"]
        
        # Fallback
        return self.intentions["mug"]

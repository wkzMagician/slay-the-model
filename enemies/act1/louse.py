"""
Louse enemies - Red and Green Louse.
Small insects with Curl Up power.
"""
import random
from typing import List, TYPE_CHECKING
from enemies.base import Enemy
from utils.types import EnemyType
from enemies.act1.louse_intentions import (
    LouseBiteIntention, 
    RedLouseGrowIntention, 
    GreenLouseSpitWebIntention
)

if TYPE_CHECKING:
    from actions.base import Action


class RedLouse(Enemy):
    """Red Louse - Gains Strength over time."""
    
    enemy_type = EnemyType.NORMAL
    
    def __init__(self):
        super().__init__(
            hp_range=(10, 15)
        )
        
        # Random damage between 5-7 (chosen at combat start)
        self._bite_damage = random.randint(5, 7)
        
        # Register intentions with random damage
        self.add_intention(LouseBiteIntention(self, self._bite_damage))
        self.add_intention(RedLouseGrowIntention(self))
        
        # Curl Up: Gains X Block when first receiving attack damage
        self._curl_up = random.randint(3, 7)
        self._curl_up_triggered = False
        
        # Add CurlUpPower to display ability
        from powers.definitions.curl_up import CurlUpPower
        self.add_power(CurlUpPower(self._curl_up))
    
    def determine_next_intention(self, floor: int = 1):
        """Determine next intention based on history.
        
        Red Louse pattern:
        - 75% Bite, 25% Grow
        - Cannot use same move 3 times in a row
        - On A17: Cannot use Grow more than 2 times in a row
        """
        # First turn: random choice
        if not self.history_intentions:
            roll = random.random()
            if roll < 0.75:
                return self.intentions["louse_bite"]
            else:
                return self.intentions["red_louse_grow"]
        
        # Count consecutive uses
        last = self.history_intentions[-1]
        consecutive_count = 0
        for intention in reversed(self.history_intentions):
            if intention == last:
                consecutive_count += 1
            else:
                break
        
        # Cannot use same move 3 times in a row
        if consecutive_count >= 2:
            if last == "louse_bite":
                return self.intentions["red_louse_grow"]
            else:
                return self.intentions["louse_bite"]
        
        # Normal pattern: 75% Bite, 25% Grow
        roll = random.random()
        if roll < 0.75:
            return self.intentions["louse_bite"]
        else:
            return self.intentions["red_louse_grow"]
    
    def on_damage_taken(self, damage: int, source=None, card=None, damage_type: str = "direct") -> List['Action']:
        """Trigger Curl Up on first attack damage."""
        actions = super().on_damage_taken(damage, source, card, damage_type)
        
        # Only trigger on attack damage and only once
        if damage_type == "attack" and not self._curl_up_triggered:
            self._curl_up_triggered = True
            from actions.combat import GainBlockAction
            actions.append(
                GainBlockAction(
                    block=self._curl_up,
                    target=self
                )
            )
        
        return actions


class GreenLouse(Enemy):
    """Green Louse - Applies Weak."""
    
    enemy_type = EnemyType.NORMAL
    
    def __init__(self):
        super().__init__(
            hp_range=(11, 17)
        )
        
        # Random damage between 5-7 (chosen at combat start)
        self._bite_damage = random.randint(5, 7)
        
        # Register intentions with random damage
        self.add_intention(LouseBiteIntention(self, self._bite_damage))
        self.add_intention(GreenLouseSpitWebIntention(self))
        
        # Curl Up: Gains X Block when first receiving attack damage
        self._curl_up = random.randint(3, 7)
        self._curl_up_triggered = False
        
        # Add CurlUpPower to display ability
        from powers.definitions.curl_up import CurlUpPower
        self.add_power(CurlUpPower(self._curl_up))
    
    def determine_next_intention(self, floor: int = 1):
        """Determine next intention based on history.
        
        Green Louse pattern:
        - 75% Bite, 25% Spit Web
        - Cannot use same move 3 times in a row
        - On A17: Cannot use Spit Web more than 2 times in a row
        """
        # First turn: random choice
        if not self.history_intentions:
            roll = random.random()
            if roll < 0.75:
                return self.intentions["louse_bite"]
            else:
                return self.intentions["green_louse_spit_web"]
        
        # Count consecutive uses
        last = self.history_intentions[-1]
        consecutive_count = 0
        for intention in reversed(self.history_intentions):
            if intention == last:
                consecutive_count += 1
            else:
                break
        
        # Cannot use same move 3 times in a row
        if consecutive_count >= 2:
            if last == "louse_bite":
                return self.intentions["green_louse_spit_web"]
            else:
                return self.intentions["louse_bite"]
        
        # Normal pattern: 75% Bite, 25% Spit Web
        roll = random.random()
        if roll < 0.75:
            return self.intentions["louse_bite"]
        else:
            return self.intentions["green_louse_spit_web"]
    
    def on_damage_taken(self, damage: int, source=None, card=None, damage_type: str = "direct") -> List['Action']:
        """Trigger Curl Up on first attack damage."""
        actions = super().on_damage_taken(damage, source, card, damage_type)
        
        # Only trigger on attack damage and only once
        if damage_type == "attack" and not self._curl_up_triggered:
            self._curl_up_triggered = True
            from actions.combat import GainBlockAction
            actions.append(
                GainBlockAction(
                    block=self._curl_up,
                    target=self
                )
            )
        
        return actions

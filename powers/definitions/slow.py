"""
SlowPower - Giant Head enemy ability.
Whenever you play a card, this enemy receives 10% more damage from Attacks.
"""
from typing import List
from actions.base import Action
from powers.base import Power, StackType
from utils.registry import register


@register("power")
class SlowPower(Power):
    """Slow power for Giant Head elite enemy.
    
    Whenever you play a card, this enemy receives 10% more damage from 
    Attacks this turn. Stacks with each card played (X * 10%).
    
    Resets at the end of each turn.
    """
    
    name = "Slow"
    description = "Whenever you play a card, receive 10% more damage from Attacks this turn."
    stack_type = StackType.INTENSITY
    is_buff = False  # Debuff from enemy's perspective (more damage taken)
    
    def __init__(self, amount: int = 0, duration: int = -1, owner=None):
        """
        Args:
            amount: Number of cards played this turn (damage multiplier)
            duration: -1 for permanent (resets each turn via on_turn_start)
        """
        super().__init__(amount=amount, duration=duration, owner=owner)
    
    def on_turn_start(self):
        """Reset the counter at the start of each turn."""
        self.amount = 0
        return
    def on_card_play(self, card, targets):
        """Increment damage multiplier when player plays a card."""
        self.amount += 1
        return
    def get_damage_taken_multiplier(self) -> float:
        """Return damage multiplier. Each card played adds 10% more damage."""
        return 1.0 + (self.amount * 0.1)

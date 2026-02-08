"""
Weak power for Ironclad cards.
Reduces damage dealt by 25% per stack.
"""
from powers.base import Power
from utils.registry import register
from utils.types import TargetType


@register("power")
class WeakPower(Power):
    """Reduce damage dealt by 25% per stack."""
    
    name = "Weak"
    description = "Reduces damage dealt by 25% per stack."
    trigger_timing = "on_damage_dealt"
    target_type = TargetType.SELF
    stackable = True
    duration = 2  # Default 2 turns
    
    def __init__(self, amount: int = 2, duration: int = 2, owner=None):
        """
        Args:
            amount: Weak stacks (default 2)
            duration: Duration in turns (default 2)
        """
        super().__init__(amount=amount, duration=duration, owner=owner)
    
    def on_damage_dealt(self, damage: int, target: any = None,
                      source: any = None, card: any = None) -> int:
        """Reduce damage dealt by 25% per stack."""
        # Weak reduces damage to 75% per stack
        return int(damage * 0.75)
    
    def tick(self) -> None:
        """Decrease duration by 1 turn."""
        if self.duration is not None and self.duration > 0:
            self.duration -= 1
            return self.duration <= 0
        return False
"""
Strength power for Ironclad cards.
Adds temporary or permanent Strength bonus.
"""
from powers.base import Power
from utils.registry import register
from utils.types import TargetType


@register("power")
class StrengthPower(Power):
    """Add Strength that modifies attack damage."""
    
    name = "Strength"
    description = "Increases attack damage by amount."
    trigger_timing = "on_damage_dealt"
    target_type = TargetType.SELF
    stackable = True
    
    def __init__(self, amount: int = 2, duration: int = 0, owner=None):
        """
        Args:
            amount: Strength to add (default 2, upgraded 4)
            duration: 0 for permanent, positive for temporary turns
        """
        super().__init__(amount=amount, duration=duration, owner=owner)
    
    def on_damage_dealt(self, damage: int, target: any = None, 
                      source: any = None, card: any = None) -> int:
        """Modify damage dealt based on Strength."""
        return damage + self.amount
    
    def tick(self) -> None:
        """Decrease duration if temporary."""
        if self.duration is not None and self.duration > 0:
            self.duration -= 1
            return self.duration <= 0
        return False

"""
Vulnerable power for Ironclad cards.
Increases damage taken by 50% per stack.
"""
from powers.base import Power
from utils.registry import register
from utils.types import TargetType


@register("power")
class VulnerablePower(Power):
    """Increase damage taken by 50% per stack."""
    
    name = "Vulnerable"
    description = "Increases damage taken by 50% per stack."
    trigger_timing = "on_damage_taken"
    target_type = TargetType.ENEMY_ALL
    stackable = True
    duration = 2  # Default 2 turns
    
    def __init__(self, amount: int = 2, duration: int = 2, owner=None):
        """
        Args:
            amount: Vulnerable stacks (default 2)
            duration: Duration in turns (default 2)
        """
        super().__init__(amount=amount, duration=duration, owner=owner)
    
    def on_damage_taken(self, damage: int, source: any = None, card: any = None,
                       player: any = None, damage_type: str = "direct") -> int:
        """Increase damage taken by 50% per stack."""
        # Vulnerable increases damage by 50% per stack
        return int(damage * (1 + 0.5 * self.amount))
    
    def tick(self) -> None:
        """Decrease duration by 1 turn."""
        if self.duration is not None and self.duration > 0:
            self.duration -= 1
            return self.duration <= 0
        return False

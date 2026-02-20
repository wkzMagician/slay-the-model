"""
Artifact power for combat effects.
Negates debuff applications.
"""
from typing import List
from powers.base import Power
from utils.registry import register


@register("power")
class ArtifactPower(Power):
    """Negates the next debuff application."""

    name = "Artifact"
    description = "Negates the next debuff."
    stackable = True
    amount_equals_duration = False
    is_buff = True

    def __init__(self, amount: int = 1, duration: int = 0, owner=None):
        """
        Args:
            amount: Number of debuffs negated (each stack negates 1 application)
            duration: 0 for permanent (doesn't decay)
        """
        super().__init__(amount=amount, duration=duration, owner=owner)

    def try_prevent_debuff(self) -> bool:
        """Try to prevent a debuff application.
        
        Returns True if the debuff was prevented (consumes 1 stack).
        """
        if self.amount > 0:
            self.amount -= 1
            print(f"[Artifact] Blocked debuff! Remaining stacks: {self.amount}")
            if self.owner and self.amount <= 0:
                self.owner.remove_power(self.name)
            return True
        return False

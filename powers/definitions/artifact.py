"""
Artifact power for combat effects.
Negates debuff applications.
"""
from typing import List
from powers.base import Power, StackType
from utils.registry import register
from tui.print_utils import tui_print


@register("power")
class ArtifactPower(Power):
    """Negates the next debuff application."""

    name = "Artifact"
    description = "Negates the next debuff."
    stack_type = StackType.INTENSITY
    is_buff = True

    def __init__(self, amount: int = 1, duration: int = -1, owner=None):
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
            tui_print(f"[Artifact] Blocked debuff! Remaining stacks: {self.amount}")
            print(f"[Artifact] Blocked debuff! Remaining stacks: {self.amount}")
            if self.owner and self.amount <= 0:
                self.owner.remove_power(self.name)
            return True
        return False

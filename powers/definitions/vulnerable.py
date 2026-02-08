"""
Vulnerable power for combat effects.
Increases damage taken by 50% per stack.
"""
from typing import Any
from powers.base import Power
from utils.registry import register


@register("power")
class VulnerablePower(Power):
    """Increase damage taken by 50% per stack."""
    
    name = "Vulnerable"
    description = "Increases damage taken by 50% per stack."
    stackable = True
    amount_equals_duration = False
    is_buff = False  # Debuff - increases damage taken
    
    def __init__(self, amount: int = 2, duration: int = 2, owner=None):
        """
        Args:
            amount: Vulnerable stacks (default 2)
            duration: Duration in turns (default 2)
        """
        super().__init__(amount=amount, duration=duration, owner=owner)
    
    def on_damage_taken(self, damage: int, source: Any = None, card: Any = None,
                       player: Any = None, damage_type: str = "direct") -> list:
        """Handle vulnerable damage modification.
        
        Note: The actual damage increase (50% per stack) is handled by
        the combat system checking for this power on the target.
        This method returns empty list as the damage calculation is done
        by reading self.amount directly.
        """
        # Vulnerable increases damage by 50% per stack
        # The actual calculation is handled in combat.py
        return []
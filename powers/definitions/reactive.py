# -*- coding: utf-8 -*-
"""
ReactivePower - Writhing Mass enemy ability
Upon receiving attack damage, changes its intent.
"""
from typing import Any, List
from actions.base import Action
from powers.base import Power, StackType
from localization import LocalStr
from utils.registry import register


@register("power")
class ReactivePower(Power):
    """
    Reactive power for Writhing Mass enemy.
    
    Upon receiving attack damage, the enemy changes its intention.
    This is a marker power - the actual intent change is handled by
    the enemy's on_physical_attack_taken method.
    """
    
    name = "Reactive"
    stack_type = StackType.INTENSITY
    is_buff = True
    
    def __init__(self, amount: int = 0, duration: int = -1, owner=None):
        """
        Args:
            amount: Not used, kept for consistency
            duration: -1 for permanent
        """
        super().__init__(amount=amount, duration=duration, owner=owner)
        self.localization_key = "powers.reactive"
        
    def on_physical_attack_taken(
        self,
        damage: int,
        source: Any = None,
        card: Any = None,
        player: Any = None,
        damage_type: str = "physical",
    ) -> None:
        """
        Called when owner takes damage.
        This power serves as a marker - the actual intent change logic
        is handled by WrithingMass.on_physical_attack_taken().
        
        """
        # This power is a marker/indicator
        # The actual intent change is handled by the enemy's physical-attack hook

    def local(self, field: str, **kwargs) -> LocalStr:
        """Get localized string for this power."""
        if field == "name":
            return LocalStr(f"{self.localization_key}.name", default=self.name)
        elif field == "description":
            return LocalStr(
                f"{self.localization_key}.description",
                default="On damage, changes its intent."
            )
        return super().local(field, **kwargs)
